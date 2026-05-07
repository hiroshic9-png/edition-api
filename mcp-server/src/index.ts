#!/usr/bin/env node
/**
 * EDITION Intelligence Platform — MCP Server
 *
 * AI agents can use these tools to:
 * - Store and recall memories with Japanese language understanding
 * - Check Japanese business regulations and compliance requirements
 * - Get tourist/visitor information for Japan
 *
 * Connects to the EDITION REST API backend.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// ── Configuration ───────────────────────────────────

const API_BASE = process.env.EDITION_API_URL || "http://localhost:8000";
const API_KEY = process.env.EDITION_API_KEY || "edition_dev_key_for_testing";

// ── HTTP helpers ────────────────────────────────────

async function apiGet(path: string): Promise<any> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

async function apiPost(path: string, body: any): Promise<any> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

// ── MCP Server ──────────────────────────────────────

const server = new McpServer({
  name: "edition",
  version: "0.1.0",
});

// ── Tool: memory_store ──────────────────────────────

server.tool(
  "memory_store",
  "会話やイベントのエピソードを永続記憶に保存します。日本語の文脈（敬語レベル、主語省略、暗黙の了解）も構造化して保持します。auto_extract=trueにすると、テキストからファクト（主語→述語→目的語の三つ組）を自動抽出します。",
  {
    content: z.string().describe("保存する内容（日本語/英語対応）"),
    session_id: z.string().optional().describe("セッション識別子"),
    role: z.enum(["user", "assistant", "system"]).default("user").describe("発話者の役割"),
    auto_extract: z.boolean().default(false).describe("LLMでファクトを自動抽出するか"),
  },
  async ({ content, session_id, role, auto_extract }) => {
    const result = await apiPost("/api/v1/memory/episodes", {
      content,
      session_id,
      role,
      auto_extract,
    });
    let text = `✅ エピソードを保存しました (ID: ${result.id})`;
    if (result.extracted_facts?.length) {
      text += `\n\n📋 自動抽出されたファクト (${result.extracted_facts.length}件):`;
      for (const f of result.extracted_facts) {
        text += `\n  - ${f.subject} → ${f.predicate} → ${f.object} (確度: ${(f.confidence * 100).toFixed(0)}%)`;
      }
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: memory_recall ─────────────────────────────

server.tool(
  "memory_recall",
  "過去の記憶をセマンティック検索で呼び出します。「前回の会議で○○部長が仰った件」のような曖昧な日本語クエリにも対応します。",
  {
    query: z.string().describe("検索クエリ（日本語/英語対応）"),
    limit: z.number().int().min(1).max(20).default(5).describe("取得件数"),
  },
  async ({ query, limit }) => {
    const result = await apiPost("/api/v1/memory/episodes/search", {
      query,
      limit,
    });
    if (!result.results?.length) {
      return { content: [{ type: "text" as const, text: "該当する記憶が見つかりませんでした。" }] };
    }
    let text = `🔍 検索結果 (${result.count}件):`;
    for (const r of result.results) {
      const dist = r.distance ? ` [類似度: ${(1 - r.distance).toFixed(2)}]` : "";
      text += `\n\n---\n${r.document}${dist}`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: memory_facts ──────────────────────────────

server.tool(
  "memory_facts",
  "現在有効なファクト（構造化された事実）の一覧を取得します。ファクトは「主語→述語→目的語」の三つ組で、確度と有効期限を持ちます。",
  {
    valid_only: z.boolean().default(true).describe("有効なファクトのみ取得するか"),
  },
  async ({ valid_only }) => {
    const result = await apiGet(`/api/v1/memory/facts?valid_only=${valid_only}`);
    if (!result.facts?.length) {
      return { content: [{ type: "text" as const, text: "保存されたファクトはありません。" }] };
    }
    let text = `📝 ファクト一覧 (${result.count}件):`;
    for (const f of result.facts) {
      const conf = f.confidence < 1.0 ? ` (確度: ${(f.confidence * 100).toFixed(0)}%)` : "";
      text += `\n  - ${f.subject} → ${f.predicate} → ${f.object}${conf}`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: memory_context ────────────────────────────

server.tool(
  "memory_context",
  "現在のセッション状態（有効な事実・合意事項のサマリー）を取得します。エージェントのプロンプトに注入して文脈を維持するために使います。",
  {
    session_id: z.string().optional().describe("セッションID（省略で全体）"),
  },
  async ({ session_id }) => {
    const params = session_id ? `?session_id=${encodeURIComponent(session_id)}` : "";
    const result = await apiGet(`/api/v1/memory/context${params}`);
    let text = `📌 コンテキストサマリー\n`;
    text += `有効なファクト: ${result.active_facts_count}件\n`;
    text += `直近のエピソード: ${result.recent_episodes_count}件\n\n`;
    text += result.summary;
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: memory_extract ────────────────────────────

server.tool(
  "memory_extract",
  "テキストからファクトを自動抽出します。日本語の敬語・主語省略・社会的階層を分析して構造化します。store=trueで永続保存。",
  {
    text: z.string().describe("ファクトを抽出するテキスト"),
    context_hint: z.string().default("").describe("コンテキストヒント（例: ビジネスミーティング）"),
    store: z.boolean().default(false).describe("抽出したファクトを永続保存するか"),
  },
  async ({ text, context_hint, store }) => {
    const result = await apiPost("/api/v1/memory/extract", {
      text,
      context_hint,
      store,
    });
    if (!result.extracted_facts?.length) {
      return { content: [{ type: "text" as const, text: "テキストからファクトを抽出できませんでした。" }] };
    }
    let response = `📋 抽出されたファクト (${result.extracted_facts.length}件):`;
    for (const f of result.extracted_facts) {
      const conf = f.confidence ? ` (確度: ${(f.confidence * 100).toFixed(0)}%)` : "";
      response += `\n  - ${f.subject} → ${f.predicate} → ${f.object}${conf}`;
    }
    response += `\n\n${result.stored ? "💾 保存済み" : "💡 未保存（store=trueで保存）"}`;
    return { content: [{ type: "text" as const, text: response }] };
  }
);

// ── Tool: regulation_check ──────────────────────────

server.tool(
  "regulation_check",
  "特定のビジネスアクションに必要な日本の規制・許認可情報を回答します。10業種の詳細データベース + 訪日旅行者向け規制に対応。",
  {
    action: z.string().describe("実行しようとしているアクション（例: 東京でレストランを開業する）"),
    industry: z.string().optional().describe("業種（省略可、自動判定）"),
    entity_type: z.enum(["foreign_company", "domestic_company", "individual", "tourist"]).default("foreign_company").describe("主体の種別"),
  },
  async ({ action, industry, entity_type }) => {
    const result = await apiPost("/api/v1/regulation/check", {
      action,
      industry,
      entity_type,
    });

    let text = "";

    if (result.category === "tourist") {
      // Tourist regulation response
      text = `🗾 訪日旅行者向け規制: ${result.matched_topic}\n\n`;
      text += `📋 概要: ${result.overview}\n\n`;
      text += `📌 主なルール:\n`;
      for (const rule of result.key_rules || []) {
        text += `  - ${rule}\n`;
      }
    } else if (result.matched_industry) {
      // Business regulation response
      text = `🏢 業種: ${result.matched_industry}\n`;
      text += `📋 必要な許認可: ${(result.licenses_required || []).join(", ")}\n`;
      text += `🏛️ 管轄: ${result.governing_body || ""}\n`;
      text += `📖 根拠法: ${result.governing_law || ""}\n\n`;
      text += `📌 要件:\n`;
      for (const req of result.requirements || []) {
        text += `  - ${req}\n`;
      }
      text += `\n⏱️ 期間: ${result.estimated_timeline || ""}`;
      text += `\n💰 費用: ${result.costs || ""}`;
      if (result.foreign_company_notes) {
        text += `\n\n🌐 外国企業向け: ${result.foreign_company_notes}`;
      }
      if (result.penalties_for_non_compliance) {
        text += `\n\n⚠️ 違反時: ${result.penalties_for_non_compliance}`;
      }
    } else {
      text = `❌ ${result.message || "該当する規制情報が見つかりませんでした。"}`;
      if (result.suggestion) text += `\n\n💡 ${result.suggestion}`;
    }

    text += `\n\n📊 確度: ${((result.confidence || 0) * 100).toFixed(0)}%`;
    text += `\n⚠️ ${result.disclaimer || "この情報は参考用です。法的助言ではありません。"}`;

    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: regulation_industries ──────────────────────

server.tool(
  "regulation_industries",
  "日本の規制データベースに登録されている業種の一覧を取得します。",
  {},
  async () => {
    const result = await apiGet("/api/v1/regulation/industries");
    let text = `🗾 対応業種一覧 (${result.count}業種):\n\n`;
    for (const ind of result.industries) {
      text += `  🏢 ${ind.industry}\n`;
      text += `     許認可: ${ind.licenses.join(", ")}\n`;
      text += `     管轄: ${ind.governing_body}\n`;
      text += `     根拠法: ${ind.governing_law}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: regulation_tourist ────────────────────────

server.tool(
  "regulation_tourist",
  "訪日旅行者向けの規制・マナー情報のカテゴリ一覧を取得します。ビザ、免税、交通、宿泊、医療、マナーの6カテゴリ。",
  {},
  async () => {
    const result = await apiGet("/api/v1/regulation/tourist");
    let text = `🗾 訪日旅行者向け規制カテゴリ (${result.count}件):\n\n`;
    for (const cat of result.categories) {
      text += `  📋 ${cat.category}: ${cat.overview}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Start ───────────────────────────────────────────

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("EDITION Intelligence Platform MCP server started (stdio)");
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
