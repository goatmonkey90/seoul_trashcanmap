# -*- coding: utf-8 -*-
"""
corrections.json을 data.json에 적용

사용법:
  python apply_corrections.py corrections.json
"""
import json, shutil, sys
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("사용법: python apply_corrections.py corrections.json")
        sys.exit(1)

    with open(sys.argv[1], encoding='utf-8') as f:
        corrections = json.load(f)

    with open('data.json', encoding='utf-8') as f:
        data = json.load(f)

    backup = f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy('data.json', backup)
    print(f"백업: {backup}")

    applied = 0
    for corr in corrections:
        for item in data:
            if (abs(item['lat'] - corr['cur_lat']) < 0.00002 and
                abs(item['lon'] - corr['cur_lon']) < 0.00002):
                item['lat']     = corr['new_lat']
                item['lon']     = corr['new_lon']
                item['geocode'] = corr.get('geocode', 'manual')
                applied += 1
                print(f"  수정: {item.get('label','?')} ({item.get('district','')})")
                break

    print(f"\n총 {applied}/{len(corrections)}건 적용")

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"-> data.json 저장 완료")
    print(f"\n다음: git add data.json && git commit -m '...' && git push")

if __name__ == "__main__":
    main()
