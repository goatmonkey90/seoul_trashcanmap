# -*- coding: utf-8 -*-
"""
공공데이터포털 전국휴지통표준데이터 API에서
강남구·송파구 쓰레기통 GPS 좌표 데이터를 가져와 data.json 생성
"""
import json, time, urllib.request, urllib.parse, sys

API_KEY = "771f57a75cdf507e03f3823d8e654caf37bc0a5dff22698b104d6244be384508"
ENDPOINT = "https://api.data.go.kr/openapi/tn_pubr_public_trash_can_api"
OUTPUT_FILE = "data.json"
PAGE_SIZE = 1000

TARGETS = {
    "강남구": {"ctpv": "서울특별시", "sgg": "강남구"},
    "송파구": {"ctpv": "서울특별시", "sgg": "송파구"},
}


def fetch_page(ctpv, sgg, page_no):
    params = {
        "serviceKey": API_KEY,
        "pageNo": str(page_no),
        "numOfRows": str(PAGE_SIZE),
        "type": "json",
        "CTPV_NM": ctpv,
        "SGG_NM": sgg,
    }
    url = ENDPOINT + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def fetch_district(district, ctpv, sgg):
    items = []
    page = 0
    while True:
        print(f"  [{district}] 페이지 {page} 요청 중...", flush=True)
        res = fetch_page(ctpv, sgg, page)

        header = res.get("response", {}).get("header", {})
        code = header.get("resultCode", "")
        if code == "30":
            print("  [X] SERVICE KEY NOT REGISTERED -- 키 활성화가 아직 안 됨")
            sys.exit(1)
        if code != "00":
            print(f"  ⚠ 응답코드: {code} — {header.get('resultMsg','')}")
            break

        body = res.get("response", {}).get("body", {})
        rows = body.get("items", [])
        if not rows:
            break

        for row in rows:
            lat = row.get("LAT") or row.get("latitude") or ""
            lon = row.get("LOT") or row.get("longitude") or ""
            if not lat or not lon:
                continue
            try:
                lat_f, lon_f = float(lat), float(lon)
            except (ValueError, TypeError):
                continue
            if lat_f == 0 or lon_f == 0:
                continue

            item = {
                "district": district,
                "label": (row.get("INSTL_PLC_NM") or "").strip(),
                "road": (row.get("LCTN_ROAD_NM") or "").strip(),
                "lat": lat_f,
                "lon": lon_f,
                "detail": (row.get("ACTL_PSTN") or "").strip(),
                "geocode": "api_official",
                "kind": (row.get("TRASH_CAN_KND") or "").strip(),
            }
            items.append(item)

        total = int(body.get("totalCount", 0))
        fetched = (page + 1) * PAGE_SIZE
        print(f"    → {len(rows)}건 (누적: {len(items)} / 전체: {total})")
        if fetched >= total:
            break
        page += 1
        time.sleep(0.15)

    return items


def main():
    all_items = []
    for district, info in TARGETS.items():
        print(f"\n{'='*40}")
        print(f" {district} 데이터 수집")
        print(f"{'='*40}")
        items = fetch_district(district, info["ctpv"], info["sgg"])
        all_items.extend(items)
        print(f"  [OK] {district}: {len(items)}건")
        time.sleep(0.3)

    # 좌표 없는 항목 통계
    no_coord = sum(1 for d in all_items if d["lat"] == 0 or d["lon"] == 0)
    print(f"\n총 {len(all_items)}건 수집 (좌표 없음: {no_coord}건)")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    print(f"\n{OUTPUT_FILE} 저장 완료!")


if __name__ == "__main__":
    main()
