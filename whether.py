# ==============================================================================
# GitHub Repository: https://github.com/rlaalsdb07/weather-reserch
# (주의: 자신의 GitHub 저장소 링크로 수정하여 제출하세요!)
# ==============================================================================

from collections import defaultdict
from datetime import datetime
import json
import requests

# Open-Meteo WMO Weather interpretation codes (WMO 날씨 코드 해석 - 보완 완료)
WMO_WEATHER_CODES = {
    0: "맑음",
    1: "주로 맑음",
    2: "구름 조금",
    3: "흐림",
    45: "안개",
    48: "서리 안개",
    51: "이슬비 (약함)",
    53: "이슬비 (보통)",
    55: "이슬비 (강함)",
    56: "어는 이슬비 (약함)",
    57: "어는 이슬비 (강함)",
    61: "비 (약함)",
    63: "비 (보통)",
    65: "비 (강함)",
    66: "어는 비 (약함)",
    67: "어는 비 (강함)",
    71: "눈 (약함)",
    73: "눈 (보통)",
    75: "눈 (강함)",
    77: "싸락눈",
    80: "소나기 (약함)",
    81: "소나기 (보통)",
    82: "소나기 (강함)",
    85: "눈 소나기 (약함)",
    86: "눈 소나기 (강함)",
    95: "뇌우",
    96: "뇌우 및 우박 (약함)",
    99: "뇌우 및 우박 (강함)",
}

# 주요 지역 위도 및 경도 좌표 데이터
CITY_COORDINATES = {
    "서울": {"lat": 37.5665, "lon": 126.9780},
    "천안": {"lat": 36.8151, "lon": 127.1139},
    "부산": {"lat": 35.1796, "lon": 129.0756},
    "대구": {"lat": 35.8714, "lon": 128.6014},
    "인천": {"lat": 37.4563, "lon": 126.7052},
    "광주": {"lat": 35.1595, "lon": 126.8526},
    "대전": {"lat": 36.3510, "lon": 127.3850},
    "울산": {"lat": 35.5384, "lon": 129.3114},
    "제주": {"lat": 33.4996, "lon": 126.5312},
}

# 도시 별칭 매핑 (사용자 입력 편의성 향상)
CITY_ALIASES = {
    "서울시": "서울",
    "서울특별시": "서울",
    "천안시": "천안",
    "부산시": "부산",
    "부산광역시": "부산",
    "대구시": "대구",
    "대구광역시": "대구",
    "인천시": "인천",
    "인천광역시": "인천",
    "광주시": "광주",
    "광주광역시": "광주",
    "대전시": "대전",
    "대전광역시": "대전",
    "울산시": "울산",
    "울산광역시": "울산",
    "제주시": "제주",
    "제주도": "제주",
    "제주특별자치도": "제주",
}


def get_weather_data(lat: float, lon: float) -> dict | None:
    """
    Open-Meteo API에서 예보 데이터 가져오기
    - current: 컴퓨터 현재 시각 기준 실시간 날씨 데이터 수신
    - hourly: 시간별 날씨 데이터 수신
    - timezone="auto": 좌표 기준 현지 시간 자동 동기화
    - forecast_days=3: 3일치 데이터만 경량 수신
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,weather_code,wind_speed_10m",
        "timezone": "auto",
        "forecast_days": 3,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"날씨 정보를 가져오는 데 실패했습니다: {e}")
        return None


def parse_and_display_weather(city_name: str, data: dict) -> list[dict]:
    """
    - 컴퓨터 현재 시각(실시간) 날씨 정보 출력
    - 3일간의 현재 시간대 / 오전 6시 / 오후 15시 날씨 정보 및 일일 최저/최고 기온 출력
    """
    now = datetime.now()
    now_hour = now.hour
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    humidities = hourly.get("relative_humidity_2m", [])
    precip_probs = hourly.get("precipitation_probability", [])
    codes = hourly.get("weather_code", [])
    wind_speeds = hourly.get("wind_speed_10m", [])

    # 날짜별 데이터 그룹화
    daily_data = defaultdict(lambda: {"hours": {}, "temps": []})

    for i, t_str in enumerate(times):
        date_str = t_str[:10]
        hour = int(t_str[11:13])
        temp = temps[i]

        daily_data[date_str]["temps"].append(temp)

        # 현재 시간대(now_hour), 6시, 15시 데이터 저장
        if hour in (6, 15, now_hour):
            daily_data[date_str]["hours"][hour] = {
                "temp": temp,
                "humidity": humidities[i],
                "precip_prob": precip_probs[i],
                "weather": WMO_WEATHER_CODES.get(codes[i], "알 수 없음"),
                "wind_speed": wind_speeds[i],
            }

    print("\n==================================================")
    print(f"📍 {city_name} 날씨 정보")
    print(f"🕒 컴퓨터 현재 시각: {now_str}")
    print("==================================================")

    # 1. 컴퓨터 현재 시각 기준 실시간 날씨 출력
    current_data = data.get("current")
    if current_data:
        curr_temp = current_data.get("temperature_2m")
        curr_weather = WMO_WEATHER_CODES.get(current_data.get("weather_code"), "알 수 없음")
        curr_humidity = current_data.get("relative_humidity_2m")
        curr_wind = current_data.get("wind_speed_10m")
        curr_precip = current_data.get("precipitation", 0.0)

        print("\n[ 🔴 실시간 현재 날씨 (지금 컴퓨터 시각 기준) ]")
        print(f"  • 상태 / 기온: {curr_weather}, {round(curr_temp) if curr_temp is not None else '-'} °C")
        print(f"  • 습도: {curr_humidity}%  |  풍속: {round(curr_wind) if curr_wind is not None else '-'} m/s  |  강수량: {curr_precip} mm")
        print("--------------------------------------------------")

    # 2. 3일치 데이터 순회
    days_keys = list(daily_data.keys())[:3]
    labels = ["오늘", "내일", "모레"]
    result_report = []

    for idx, date_key in enumerate(days_keys):
        day_info = daily_data[date_key]
        label = labels[idx] if idx < len(labels) else f"{idx}일 후"
        month_day = f"{date_key[5:7]}.{date_key[8:10]}."

        print(f"\n📅 {label} ({month_day})")
        print("--------------------------------------------------")

        min_t_raw = min(day_info["temps"])
        max_t_raw = max(day_info["temps"])

        day_dict = {
            "date": date_key,
            "label": label,
            "current_hour_weather": day_info["hours"].get(now_hour),
            "morning_06": day_info["hours"].get(6),
            "afternoon_15": day_info["hours"].get(15),
            "min_temp": min_t_raw,
            "max_temp": max_t_raw,
        }
        if idx == 0 and current_data:
            day_dict["realtime_current"] = current_data

        result_report.append(day_dict)

        # 현재 컴퓨터 시간대 예보 출력
        if now_hour in day_info["hours"]:
            h_now = day_info["hours"][now_hour]
            tag = f"현재 시각 ({now_hour:02d}:00)" if idx == 0 else f"동시간대 ({now_hour:02d}:00)"
            print(f"  ⏱️ {tag}")
            print(f"     날씨: {h_now['weather']}")
            print(f"     기온: {round(h_now['temp'])} °C")
            print(f"     강수확률: {h_now['precip_prob']}%")
            print(f"     습도: {h_now['humidity']}%")
            print(f"     풍속: {round(h_now['wind_speed'])} m/s")

        # 오전 06:00 (현재 시각과 겹치지 않을 때 출력)
        if 6 in day_info["hours"] and now_hour != 6:
            h6 = day_info["hours"][6]
            print("  🏮 오전 06:00")
            print(f"     날씨: {h6['weather']}")
            print(f"     기온: {round(h6['temp'])} °C")
            print(f"     강수확률: {h6['precip_prob']}%")
            print(f"     습도: {h6['humidity']}%")
            print(f"     풍속: {round(h6['wind_speed'])} m/s")

        # 오후 15:00 (현재 시각과 겹치지 않을 때 출력)
        if 15 in day_info["hours"] and now_hour != 15:
            h15 = day_info["hours"][15]
            print("  🌆 오후 15:00")
            print(f"     날씨: {h15['weather']}")
            print(f"     기온: {round(h15['temp'])} °C")
            print(f"     강수확률: {h15['precip_prob']}%")
            print(f"     습도: {h15['humidity']}%")
            print(f"     풍속: {round(h15['wind_speed'])} m/s")

        print(f"\n  🏷️ 일일 기온: 최저 {round(min_t_raw)} °C / 최고 {round(max_t_raw)} °C")

    print("\n==================================================")
    return result_report


def main():
    now = datetime.now()
    print("🌻 날씨 예보 프로그램 (Open-Meteo API)")
    print(f"컴퓨터 현재 시각({now.strftime('%H:%M')}) 실시간 날씨 및 3일간 예보를 제공합니다.\n")
    print("--------------------------------------------------")

    city_input = input("날씨를 확인할 지역을 입력하세요 (기본값: 서울): ").strip()
    if not city_input:
        city_input = "서울"

    # 별칭 처리 (예: '서울시', '서울특별시' -> '서울')
    city = CITY_ALIASES.get(city_input, city_input)

    if city in CITY_COORDINATES:
        lat = CITY_COORDINATES[city]["lat"]
        lon = CITY_COORDINATES[city]["lon"]
    else:
        # 등록되지 않은 지역일 경우 기본 지역(천안)으로 폴백
        print(f"'{city_input}' 좌표를 찾을 수 없어 기본 지역(천안)으로 설정합니다.")
        city = "천안"
        lat, lon = CITY_COORDINATES["천안"]["lat"], CITY_COORDINATES["천안"]["lon"]

    print(f"\n📍 {city} (위도: {lat}, 경도: {lon}) 의 날씨 정보를 가져옵니다...")

    raw_data = get_weather_data(lat, lon)
    if raw_data:
        report = parse_and_display_weather(city, raw_data)

        # JSON 저장 여부 확인
        print()
        save_json = input("날씨 정보를 JSON 파일로 저장하시겠습니까? (y/n): ").strip().lower()
        if save_json == "y":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"weather_{city}_{timestamp}.json"
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(report, f, ensure_ascii=False, indent=4)
                print(f"날씨 정보가 '{filename}' 파일로 저장되었습니다.")
            except OSError as e:
                print(f"파일 저장 중 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()