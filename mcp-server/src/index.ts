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

const API_BASE = process.env.EDITION_API_URL || "https://api.edition.sh";
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
  version: "0.2.0",
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

// ── Tool: protocol_check ────────────────────────────

server.tool(
  "protocol_check",
  "日本のビジネスプロトコル（根回し、稟議、報連相、名刺交換、席順、贈答）を検索します。",
  {
    query: z.string().describe("検索クエリ（例: '名刺交換の作法', '根回し'）"),
  },
  async ({ query }) => {
    const result = await apiPost("/api/v1/protocol/check", { query });
    if (!result.protocol_id && !result.name_ja) {
      return { content: [{ type: "text" as const, text: `❌ '${query}' に該当するプロトコルが見つかりませんでした。` }] };
    }
    let text = `🤝 ${result.name_ja || result.protocol_id}\n`;
    text += `📋 ${result.summary || ""}\n`;
    if (result.how_to) {
      text += `\n📌 手順:\n`;
      for (const step of result.how_to) {
        text += `  ${step.step}. ${step.action}: ${step.detail}\n`;
      }
    }
    if (result.protocol) {
      text += `\n📌 手順:\n`;
      for (const step of result.protocol) {
        text += `  ${step.step}. ${step.action}: ${step.detail}\n`;
      }
    }
    text += `\n📊 確度: ${((result.confidence || 0) * 100).toFixed(0)}%`;
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: protocol_list ─────────────────────────────

server.tool(
  "protocol_list",
  "日本のビジネスプロトコルの一覧を取得します。",
  {},
  async () => {
    const result = await apiGet("/api/v1/protocol/list");
    let text = `🤝 プロトコル一覧 (${result.count}件):\n\n`;
    for (const p of result.protocols) {
      text += `  • ${p.name_ja} (${p.name_en}) — ${p.importance}\n    ${p.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: calendar_check ────────────────────────────

server.tool(
  "calendar_check",
  "日本のビジネスカレンダー情報を検索します。祝日、決算期、贈答シーズン、行政締切、季節性ビジネスの5カテゴリ。",
  {
    query: z.string().describe("検索クエリ（例: '開業のベストタイミング', 'GW', '確定申告の締切'）"),
  },
  async ({ query }) => {
    const result = await apiPost("/api/v1/calendar/check", { query });
    if (!result.category_id) {
      return { content: [{ type: "text" as const, text: `❌ '${query}' に該当するカレンダー情報が見つかりませんでした。` }] };
    }
    let text = `📅 ${result.name_ja}\n📋 ${result.summary}\n`;
    text += `\n📊 確度: ${((result.confidence || 0) * 100).toFixed(0)}%`;
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: calendar_list ─────────────────────────────

server.tool(
  "calendar_list",
  "日本のビジネスカレンダーの全カテゴリ一覧を取得します。",
  {},
  async () => {
    const result = await apiGet("/api/v1/calendar/list");
    let text = `📅 カレンダーカテゴリ一覧 (${result.count}件):\n\n`;
    for (const c of result.categories) {
      text += `  • ${c.name_ja} (${c.name_en})\n    ${c.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: regional_check ────────────────────────────

server.tool(
  "regional_check",
  "日本の地域別ビジネス情報を検索します。主要都市の特性、自治体の助成金・補助金、地域条例、商慣習の違い。",
  {
    query: z.string().describe("検索クエリ（例: '大阪の飲食店条例', '東京のスタートアップ助成金'）"),
  },
  async ({ query }) => {
    const result = await apiPost("/api/v1/regional/check", { query });
    if (!result.category_id) {
      return { content: [{ type: "text" as const, text: `❌ '${query}' に該当する地域情報が見つかりませんでした。` }] };
    }
    let text = `🗺️ ${result.name_ja}\n📋 ${result.summary}\n`;
    text += `\n📊 確度: ${((result.confidence || 0) * 100).toFixed(0)}%`;
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: regional_list ─────────────────────────────

server.tool(
  "regional_list",
  "日本の地域別ビジネス情報の全カテゴリ一覧を取得します。",
  {},
  async () => {
    const result = await apiGet("/api/v1/regional/list");
    let text = `🗺️ 地域情報カテゴリ一覧 (${result.count}件):\n\n`;
    for (const c of result.categories) {
      text += `  • ${c.name_ja} (${c.name_en})\n    ${c.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: organization_check ────────────────────────

server.tool(
  "organization_check",
  "日本の組織構造・商慣行を検索します。役職体系、系列、支払慣行、契約慣行、業界団体。",
  {
    query: z.string().describe("検索クエリ（例: '支払いサイトの標準', '契約書の印鑑', '部長と課長の違い'）"),
  },
  async ({ query }) => {
    const result = await apiPost("/api/v1/organization/check", { query });
    if (!result.category_id) {
      return { content: [{ type: "text" as const, text: `❌ '${query}' に該当する組織情報が見つかりませんでした。` }] };
    }
    let text = `🏛️ ${result.name_ja}\n📋 ${result.summary}\n`;
    text += `\n📊 確度: ${((result.confidence || 0) * 100).toFixed(0)}%`;
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: organization_list ─────────────────────────

server.tool(
  "organization_list",
  "日本の組織構造・商慣行の全カテゴリ一覧を取得します。",
  {},
  async () => {
    const result = await apiGet("/api/v1/organization/list");
    let text = `🏛️ 組織情報カテゴリ一覧 (${result.count}件):\n\n`;
    for (const c of result.categories) {
      text += `  • ${c.name_ja} (${c.name_en})\n    ${c.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: foreign_entry_check ───────────────────────

server.tool(
  "foreign_entry_check",
  "外国企業・外国人の日本進出に必要な基盤知識を検索します。法人設立、経営管理ビザ、銀行口座開設、物件探し、税務届出の5カテゴリ。",
  {
    query: z.string().describe("検索クエリ（例: '法人設立の手順', 'ビザ取得', '銀行口座開設'）"),
  },
  async ({ query }) => {
    const result = await apiPost("/api/v1/foreign-entry/check", { query });
    if (!result.category_id) {
      return { content: [{ type: "text" as const, text: `❌ '${query}' に該当する進出情報が見つかりませんでした。` }] };
    }
    let text = `🌐 ${result.name_ja}\n📋 ${result.summary}\n`;
    if (result.procedures) {
      text += `\n📌 手順 (${result.procedures.length}ステップ):\n`;
      for (const s of result.procedures) {
        text += `  ${s.step}. ${s.what}: ${s.detail}\n`;
      }
    }
    text += `\n📊 確度: ${((result.confidence || 0) * 100).toFixed(0)}%`;
    text += `\n⚠️ ${result.disclaimer || "この情報は一般的なガイダンスです。"}`;
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: foreign_entry_list ────────────────────────

server.tool(
  "foreign_entry_list",
  "外国企業・外国人の日本進出に関する知識カテゴリの一覧を取得します。",
  {},
  async () => {
    const result = await apiGet("/api/v1/foreign-entry/list");
    let text = `🌐 日本進出カテゴリ一覧 (${result.count}件):\n\n`;
    for (const c of result.categories) {
      text += `  • ${c.name_ja} (${c.name_en})\n    ${c.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: travel_search ─────────────────────────────

server.tool(
  "travel_search",
  "日本の旅行・観光に関する知識を検索します。交通（新幹線・ICカード・タクシー）、宿泊（旅館マナー・ホテル）、飲食（ラーメン地域差・箸マナー・チップ不要）、実用情報（SIM・ATM・緊急連絡先・マナー）。",
  {
    query: z.string().describe("検索クエリ（例: '新幹線の乗り方', '旅館のマナー', 'ラーメンの食べ方'）"),
  },
  async ({ query }) => {
    const result = await apiPost("/api/v1/travel/search", { query });
    if (!result.results?.length) {
      return { content: [{ type: "text" as const, text: `❌ '${query}' に該当する旅行情報が見つかりませんでした。` }] };
    }
    let text = `✈️ 旅行情報 (${result.total_matches}件ヒット):\n\n`;
    for (const r of result.results) {
      text += `  📌 ${r.name_ja} (${r.name_en})\n     ${r.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: travel_list ───────────────────────────────

server.tool(
  "travel_list",
  "日本の旅行知識のトピック一覧を取得します。",
  {},
  async () => {
    const result = await apiGet("/api/v1/travel/list");
    let text = `✈️ 旅行トピック一覧 (${result.total}件):\n\n`;
    for (const t of result.topics) {
      text += `  • ${t.name_ja} (${t.name_en})\n    ${t.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: entertainment_search ──────────────────────

server.tool(
  "entertainment_search",
  "日本のエンターテインメント・ポップカルチャーに関する知識を検索します。推し活（チケット取得・転売法）、アニメ聖地巡礼、ライブマナー（ペンライト・コール）、季節イベント（花見・花火・初詣）。",
  {
    query: z.string().describe("検索クエリ（例: '推し活のチケット購入', 'コミケの参加方法', '花見のマナー'）"),
  },
  async ({ query }) => {
    const result = await apiPost("/api/v1/entertainment/search", { query });
    if (!result.results?.length) {
      return { content: [{ type: "text" as const, text: `❌ '${query}' に該当するエンタメ情報が見つかりませんでした。` }] };
    }
    let text = `🎭 エンタメ情報 (${result.total_matches}件ヒット):\n\n`;
    for (const r of result.results) {
      text += `  📌 ${r.name_ja} (${r.name_en})\n     ${r.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: entertainment_list ────────────────────────

server.tool(
  "entertainment_list",
  "日本のエンタメ知識のトピック一覧を取得します。",
  {},
  async () => {
    const result = await apiGet("/api/v1/entertainment/list");
    let text = `🎭 エンタメトピック一覧 (${result.total}件):\n\n`;
    for (const t of result.topics) {
      text += `  • ${t.name_ja} (${t.name_en})\n    ${t.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: daily_life_search ─────────────────────────

server.tool(
  "daily_life_search",
  "日本の日常生活に関する知識を検索します。住所・郵便システム、ゴミ分別ルール、公共料金（電気・ガス・水道・NHK）、医療・健康保険制度。外国人が日本で生活するために必要な実用知識。",
  {
    query: z.string().describe("検索クエリ（例: 'ゴミの分別方法', '健康保険の加入', '引っ越しの手続き'）"),
  },
  async ({ query }) => {
    const result = await apiPost("/api/v1/daily-life/search", { query });
    if (!result.results?.length) {
      return { content: [{ type: "text" as const, text: `❌ '${query}' に該当する日常生活情報が見つかりませんでした。` }] };
    }
    let text = `🏠 日常生活情報 (${result.total_matches}件ヒット):\n\n`;
    for (const r of result.results) {
      text += `  📌 ${r.name_ja} (${r.name_en})\n     ${r.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: daily_life_list ──────────────────────────

server.tool(
  "daily_life_list",
  "日本の日常生活知識のトピック一覧を取得します。",
  {},
  async () => {
    const result = await apiGet("/api/v1/daily-life/list");
    let text = `🏠 日常生活トピック一覧 (${result.total}件):\n\n`;
    for (const t of result.topics) {
      text += `  • ${t.name_ja} (${t.name_en})\n    ${t.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: language_search ──────────────────────────

server.tool(
  "language_search",
  "日本語の構造的知識を検索します。敬語体系（尊敬語・謙譲語・丁寧語）、助数詞（数え方）、名前・住所の構造パターン、ビジネス日本語（電話応対・クッション言葉・メールテンプレート）。",
  {
    query: z.string().describe("検索クエリ（例: '敬語の使い方', '助数詞の一覧', 'ビジネスメールの書き方'）"),
  },
  async ({ query }) => {
    const result = await apiPost("/api/v1/language/search", { query });
    if (!result.results?.length) {
      return { content: [{ type: "text" as const, text: `❌ '${query}' に該当する日本語情報が見つかりませんでした。` }] };
    }
    let text = `🗾 日本語知識 (${result.total_matches}件ヒット):\n\n`;
    for (const r of result.results) {
      text += `  📌 ${r.name_ja} (${r.name_en})\n     ${r.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: language_list ────────────────────────────

server.tool(
  "language_list",
  "日本語知識のトピック一覧を取得します。",
  {},
  async () => {
    const result = await apiGet("/api/v1/language/list");
    let text = `🗾 日本語トピック一覧 (${result.total}件):\n\n`;
    for (const t of result.topics) {
      text += `  • ${t.name_ja} (${t.name_en})\n    ${t.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: food_search ──────────────────────────────

server.tool(
  "food_search",
  "日本の食文化に関する知識を検索します。食事マナー（箸のタブー・乾杯・割り勘）、料理分類（懐石・定食・ラーメン・郷土料理）、飲食店ガイド（食券機・居酒屋・回転寿司・おまかせ）、アレルギー・食制限（ハラル・ベジタリアン対応）。",
  {
    query: z.string().describe("検索クエリ（例: '箸のマナー', 'ハラル対応レストラン', '回転寿司の注文方法'）"),
  },
  async ({ query }) => {
    const result = await apiPost("/api/v1/food/search", { query });
    if (!result.results?.length) {
      return { content: [{ type: "text" as const, text: `❌ '${query}' に該当する食文化情報が見つかりませんでした。` }] };
    }
    let text = `🍣 食文化情報 (${result.total_matches}件ヒット):\n\n`;
    for (const r of result.results) {
      text += `  📌 ${r.name_ja} (${r.name_en})\n     ${r.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: food_list ────────────────────────────────

server.tool(
  "food_list",
  "日本の食文化知識のトピック一覧を取得します。",
  {},
  async () => {
    const result = await apiGet("/api/v1/food/list");
    let text = `🍣 食文化トピック一覧 (${result.total}件):\n\n`;
    for (const t of result.topics) {
      text += `  • ${t.name_ja} (${t.name_en})\n    ${t.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: disaster_search ──────────────────────────

server.tool(
  "disaster_search",
  "日本の災害・安全に関する知識を検索します。地震（震度スケール・緊急地震速報・耐震基準）、台風・水害（警戒レベル・計画運休）、緊急連絡先（110/119/多言語対応）、防災準備（防災バッグ・ハザードマップ・避難所マナー）。",
  {
    query: z.string().describe("検索クエリ（例: '地震が来たらどうする', '緊急連絡先', '防災バッグの中身'）"),
  },
  async ({ query }) => {
    const result = await apiPost("/api/v1/disaster/search", { query });
    if (!result.results?.length) {
      return { content: [{ type: "text" as const, text: `❌ '${query}' に該当する災害・安全情報が見つかりませんでした。` }] };
    }
    let text = `⚠️ 災害・安全情報 (${result.total_matches}件ヒット):\n\n`;
    for (const r of result.results) {
      text += `  📌 ${r.name_ja} (${r.name_en})\n     ${r.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: disaster_list ────────────────────────────

server.tool(
  "disaster_list",
  "日本の災害・安全知識のトピック一覧を取得します。",
  {},
  async () => {
    const result = await apiGet("/api/v1/disaster/list");
    let text = `⚠️ 災害・安全トピック一覧 (${result.total}件):\n\n`;
    for (const t of result.topics) {
      text += `  • ${t.name_ja} (${t.name_en})\n    ${t.summary}\n\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Tool: search ────────────────────────────────────

server.tool(
  "search",
  "EDITION全14ドメインを横断検索します。1回のリクエストで規制・プロトコル・カレンダー・地域・組織・進出手続き・旅行・エンタメ・日常生活・日本語・食文化・災害安全の全12ドメインを同時検索。",
  {
    query: z.string().describe("検索クエリ（例: '大阪で飲食店を開業', '地震の避難方法', '敬語の使い方'）"),
  },
  async ({ query }) => {
    const result = await apiPost("/api/v1/search", { query });
    let text = `🔍 横断検索結果: ${result.domains_matched}/${result.domains_searched} ドメインでヒット\n\n`;
    for (const [domain, data] of Object.entries(result.results) as [string, any][]) {
      const name = data.name_ja || data.industry || domain;
      text += `  ✅ ${domain}: ${name} (確度: ${((data.confidence || 0) * 100).toFixed(0)}%)\n`;
      if (data.summary) text += `     ${data.summary}\n`;
    }
    if (result.domains_matched === 0) {
      text += `  ❌ 該当する情報が見つかりませんでした。\n`;
    }
    return { content: [{ type: "text" as const, text }] };
  }
);

// ── Resources ───────────────────────────────────────

server.resource(
  "domains",
  "edition://domains",
  {
    description: "All 14 knowledge domains with descriptions, endpoints, and coverage status",
    mimeType: "application/json",
  },
  async () => {
    const domains = [
      { id: "memory", name: "Persistent Memory", endpoint: "/api/v1/memory", tools: 5, layers: ["rules", "context"] },
      { id: "regulation", name: "Business Regulations", endpoint: "/api/v1/regulation", tools: 3, layers: ["rules", "context", "experience"] },
      { id: "protocol", name: "Business Protocols", endpoint: "/api/v1/protocol", tools: 2, layers: ["rules", "context", "experience"] },
      { id: "calendar", name: "Business Calendar", endpoint: "/api/v1/calendar", tools: 2, layers: ["rules", "context", "experience"] },
      { id: "regional", name: "Regional Intelligence", endpoint: "/api/v1/regional", tools: 2, layers: ["rules", "context", "experience"] },
      { id: "organization", name: "Organizational Structures", endpoint: "/api/v1/organization", tools: 2, layers: ["rules", "context", "experience"] },
      { id: "foreign_entry", name: "Foreign Market Entry", endpoint: "/api/v1/foreign-entry", tools: 2, layers: ["rules", "context", "experience"] },
      { id: "travel", name: "Travel Intelligence", endpoint: "/api/v1/travel", tools: 2, layers: ["rules", "context", "experience"] },
      { id: "entertainment", name: "Entertainment & Pop Culture", endpoint: "/api/v1/entertainment", tools: 2, layers: ["rules", "context", "experience"] },
      { id: "daily_life", name: "Daily Life", endpoint: "/api/v1/daily-life", tools: 2, layers: ["rules", "context"] },
      { id: "language", name: "Japanese Language", endpoint: "/api/v1/language", tools: 2, layers: ["rules", "context"] },
      { id: "food", name: "Food Culture", endpoint: "/api/v1/food", tools: 2, layers: ["rules", "context", "experience"] },
      { id: "disaster", name: "Disaster & Safety", endpoint: "/api/v1/disaster", tools: 2, layers: ["rules", "context"] },
      { id: "search", name: "Cross-Domain Search", endpoint: "/api/v1/search", tools: 1, layers: ["rules", "context", "experience"] },
    ];
    return {
      contents: [
        {
          uri: "edition://domains",
          mimeType: "application/json",
          text: JSON.stringify({ total: domains.length, total_tools: 31, domains }, null, 2),
        },
      ],
    };
  }
);

server.resource(
  "quality",
  "edition://quality",
  {
    description: "Trust Anchor quality scores — verified data coverage, source reliability, and 3-layer completeness for each domain",
    mimeType: "application/json",
  },
  async () => {
    try {
      const data = await apiGet("/api/v1/analytics/quality");
      return {
        contents: [
          {
            uri: "edition://quality",
            mimeType: "application/json",
            text: JSON.stringify(data, null, 2),
          },
        ],
      };
    } catch {
      return {
        contents: [
          {
            uri: "edition://quality",
            mimeType: "application/json",
            text: JSON.stringify({ error: "Quality endpoint unavailable" }),
          },
        ],
      };
    }
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
