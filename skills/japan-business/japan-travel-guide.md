---
name: japan-travel-guide
version: 1.0.0
description: "Comprehensive travel intelligence for visitors to Japan — transportation, dining, entertainment, and safety"
domain: japan
categories: [travel, food, entertainment, disaster]
tools_required:
  - travel_search
  - travel_list
  - food_search
  - entertainment_search
  - disaster_search
triggers:
  - "visit Japan"
  - "trip to Tokyo"
  - "Japanese restaurant"
  - "shinkansen bullet train"
  - "earthquake safety Japan"
  - "anime pilgrimage"
  - "ramen etiquette"
source: https://api.edition.sh
source_authorities:
  - "国土交通省 (MLIT) — Transportation"
  - "観光庁 (JTA) — Tourism"
  - "気象庁 (JMA) — Disaster warnings"
  - "消防庁 — Emergency services"
author: EDITION Intelligence Platform
last_verified: "2026-05-10"
---

# Japan Travel Guide

## When to Use This Skill

Activate when the user or agent needs to:
- Plan transportation within Japan
- Navigate dining customs and restaurant types
- Attend entertainment events or visit cultural sites
- Understand safety procedures for natural disasters
- Prepare for cultural interactions as a tourist

## Standard Operating Procedure

### Pre-Trip Briefing
1. Use `travel_search` with "practical_info" for essentials (SIM, cash, IC cards)
2. Use `disaster_search` with "earthquake" for safety briefing
3. Use `food_search` with "dining_etiquette" for meal preparation
4. Use `entertainment_search` with "seasonal_events" for what's happening

### Transportation Navigation
Use `travel_search` with "transportation":
- **Between cities**: Shinkansen (bullet train) — reserve via SmartEX app
- **Within cities**: IC card (Suica/PASMO) — tap-in/tap-out for all transit
- **Airports**: Narita Express or Limousine Bus for NRT; monorail for HND

### Dining Guidance
1. Use `food_search` with "restaurant_guide" for ordering systems
2. Use `food_search` with "dining_etiquette" for table manners
3. Use `food_search` with "dietary_restrictions" if applicable

### Emergency Response
Use `disaster_search` with specific disaster type:
- Earthquake → Drop, Cover, Hold On → check NHK/Yahoo!防災
- Typhoon → 5-level warning system → check 計画運休 for trains

## Key Knowledge

### Transportation Essentials
| System | Use Case | Key Tip |
|--------|----------|---------|
| Shinkansen | City-to-city | Japan Rail Pass or SmartEX |
| IC Card (Suica) | All local transit + convenience stores | Load at any station |
| Taxi | Short distances, late night | Auto-opening doors, no tipping |

### Dining Rules — The Non-Negotiables
- **Chopstick taboos**: Never stick vertically in rice (funeral ritual), never pass food chopstick-to-chopstick
- **Slurping**: Acceptable and expected for noodles
- **Tipping**: Do NOT tip. It can cause confusion or offense
- **Itadakimasu**: Say before eating (gratitude for the meal)
- **Oshibori**: Hot towel is for hands only, not face

### Restaurant Types
| Type | System | What to Know |
|------|--------|--------------|
| Ramen shop | 食券機 (ticket machine) | Buy ticket → hand to staff |
| Izakaya | Table order (tablet/verbal) | Otoshi (お通し) cover charge is automatic |
| Sushi counter | Omakase or à la carte | Never add wasabi to soy sauce at high-end |
| Conveyor sushi | Take plates from belt | Price by plate color |
| Convenience store | Self-service | Eat-in tax 10% vs take-out 8% |

### Emergency Numbers
| Number | Service | Language |
|--------|---------|----------|
| **110** | Police | Japanese (interpreter available) |
| **119** | Fire/Ambulance | Japanese (interpreter available) |
| **#7119** | Medical consultation | Some English |
| **050-3816-2787** | Japan Visitor Hotline | EN/CN/KR 24h |

### Earthquake Quick Guide
1. **During shaking**: Drop, Cover, Hold On. Stay away from windows
2. **After shaking**: Check for gas leaks. Put on shoes (broken glass)
3. **Tsunami risk**: If near coast and shaking >1min, move to high ground immediately
4. **Communication**: Use 災害用伝言ダイヤル (171) for emergency messages

## Common Pitfalls

> ⚠️ **Cash is still king**: Many small restaurants, temples, and rural areas are cash-only. Carry ¥10,000-20,000 in small bills.

> ⚠️ **Last train**: Trains stop around midnight. Missing the last train means taxi (expensive) or manga cafe until 5am first train.

> ⚠️ **Quiet cars**: Shinkansen has designated quiet cars (usually car 1). No phone calls, no loud conversation.

> ⚠️ **Temple/shrine etiquette**: Remove shoes when entering buildings. Bow at torii gates. Wash hands at temizuya.
