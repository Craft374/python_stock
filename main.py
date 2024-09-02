import random  # type: ignore
import platform
import os

def clear_screen():
    """화면을 지우는 함수"""
    # 운영 체제에 따라 다른 명령어 사용
    if platform.system() == "Windows":
        os.system('cls')  # Windows에서 화면 지우기
    else:
        os.system('clear')  # Unix 계열 시스템에서 화면 지우기

stocks = {}  # 주식 정보를 저장할 딕셔너리
clear_screen()
# 초기 자본금 설정
balance = 1000000  # 시작 자본금 100만원

# 주식 상태 출력 함수 수정
def display_status():
    """현재 자산 상태를 출력하는 함수"""
    print(f"\n현재 자본금: {format_currency(balance)}원")
    print(f"한글 표현: {number_to_korean(balance)}원")
    print("\n주식 정보:")

    for eng_name, stock in stocks.items():
        old_price = stock.get('previous_price', stock['price'])
        new_price = stock['price']

        if old_price != new_price:
            percentage_change = ((new_price - old_price) / old_price) * 100
        else:
            percentage_change = 0

        # 색상 설정
        if percentage_change > 0:
            color = '\033[91m'  # 빨간색
        elif percentage_change < 0:
            color = '\033[94m'  # 파란색
        else:
            color = '\033[0m'  # 기본 색상

        # 주식의 영어 이름과 함께 출력
        print(
            f"{stock['name']} ({eng_name}): 주가: {format_currency(new_price)}원, 보유 주식: {stock['shares']}주, 등락: {color}{percentage_change:.2f}%\033[0m")

    print()  # 빈 줄 추가


def format_currency(amount):
    #자본금과 주가에 쉼표를 추가하여 포맷하는 함수
    return "{:,}".format(amount)


def buy_stock(company, shares):
    """주식을 구매하는 함수"""
    global balance

    # 회사 이름에 맞는 주식 정보를 찾는다
    stock = stocks.get(company)
    if stock is None:
        print("잘못된 회사 이름입니다.")
        return

    price = stock['price']

    # 자본금이 충분한지 확인
    if balance >= shares * price:
        balance -= shares * price
        stock['shares'] += shares  # 주식 보유량 업데이트
        print(f"{stock['name']} 주식 {shares}주를 구매하셨습니다.")
    else:
        print("잔액이 부족합니다!")

def sell_stock(company, shares):
    """주식을 판매하는 함수"""
    global balance

    # 회사 이름에 맞는 주식 정보를 찾는다
    stock = stocks.get(company)
    if stock is None:
        print("잘못된 회사 이름입니다.")
        return

    if shares > stock['shares']:
        print("보유한 주식이 부족합니다.")
        return

    price = stock['price']
    stock['shares'] -= shares  # 주식 보유량 업데이트
    balance += shares * price
    print(f"{stock['name']} 주식 {shares}주를 판매하셨습니다.")


def update_stock_price():
    """주가를 각 주식의 최대 등락 범위를 기반으로 랜덤하게 변경하는 함수"""
    global stocks

    for eng_name, stock in stocks.items():
        # 현재 가격을 이전 가격으로 저장
        stock['previous_price'] = stock['price']

        old_price = stock['price']
        change = random.randint(stock['min_change'], stock['max_change'])
        stock['price'] += change
        if stock['price'] < 1000:
            stock['price'] = 1000


def save_game():
    with open('save.txt', 'w', encoding='utf-8') as file:
        # 첫 줄에 자본금 저장
        file.write(f"{balance}\n")

        # 주식 정보 저장
        for eng_name, stock in stocks.items():
            file.write(f"{stock['name']}: {stock['price']}: {stock['shares']}\n")
    print("게임이 저장되었습니다.")

def load_game():
    global balance
    try:
        with open('save.txt', 'r', encoding='utf-8') as file:
            # 첫 줄에서 자본금 불러오기
            balance = int(file.readline().strip())

            # 나머지 줄에서 주식 정보 불러오기
            for line in file:
                name, rest = line.strip().split(": ", 1)
                price, shares = rest.split(":")
                price = int(price)
                shares = int(shares)

                # 주식 이름에 해당하는 가격과 보유량을 갱신
                for stock in stocks.values():
                    if stock['name'] == name:
                        stock['price'] = price
                        stock['shares'] = shares
                        break
        print("게임이 로드되었습니다.")
    except FileNotFoundError:
        print("저장된 게임이 없습니다.")

def load_stock_data():
    global stocks
    try:
        with open('stock.txt', 'r', encoding='utf-8') as file:
            for line in file:
                # 파일의 각 줄을 읽고 공백으로 분리
                name, eng_name, initial_price, change_range = line.strip().split()
                initial_price = int(initial_price)

                # 등락 범위 분리
                min_change, max_change = map(int, change_range.split('~'))

                # 딕셔너리에 주식 정보 저장
                stocks[eng_name] = {
                    'name': name,
                    'price': initial_price,
                    'min_change': min_change,
                    'max_change': max_change,
                    'shares': 0  # 보유 주식 초기화
                }
    except FileNotFoundError:
        print("stock.txt 파일이 없습니다. 기본 주식 정보를 사용합니다.")

def number_to_korean(number):
    """숫자를 한글 단위로 변환하는 함수"""
    units = [
        (10**36, '간'),
        (10**32, '구'),
        (10**28, '양'),
        (10**24, '자'),
        (10**20, '해'),
        (10**16, '경'),
        (10**12, '조'),
        (10**8, '억'),
        (10**4, '만'),
        (10**0, '')  # 기본 단위
    ]

    if number == 0:
        return "0"

    result = []
    for value, unit in units:
        if number >= value:
            count = number // value
            if count > 0 or len(result) > 0:  # 앞에 단위가 있는 경우에도 출력
                result.append(f"{count}{unit}")
            number %= value

    return ' '.join(result)

def main():
    global balance
    print("주식 게임에 오신 것을 환영합니다!")
    load_stock_data()
    display_status()
    while True:
        # display_status()
        command = input(
            "행동을 입력하세요 (예: buy, sell, update, save, load, help, exit): ").strip().lower()

        if command.startswith("buy"):
            try:
                _, company, shares = command.split()
                shares = int(shares)
                buy_stock(company, shares)
            except ValueError:
                print("올바른 형식으로 입력하세요: buy [회사명] [주식수]")

        elif command.startswith("sell"):
            try:
                _, company, shares = command.split()
                shares = int(shares)
                sell_stock(company, shares)
            except ValueError:
                print("올바른 형식으로 입력하세요: sell [회사명] [주식수]")

        elif command.startswith("help"):
            print("\033[36m도움말\033[0m")
            print("\033[36m모든 회사명은 영어로 작성해야 합니다\033[0m")
            print("\033[36mbuy\033[0m: \033[32mbuy [회사명] [주식수]로 주식을 구매할 수 있습니다\033[0m")
            print("\033[36msell\033[0m: \033[32msell [회사명] [주식수]로 주식을 판매할 수 있습니다\033[0m")
            print("\033[36mupdate\033[0m: \033[32mupdate [횟수]로 새로고침을 할 수 있습니다\033[0m")
            print("\033[36msave\033[0m: \033[32msave로 현재 돈과 주가, 주식수를 저장 할 수 있습니다\033[0m")
            print("\033[36mload\033[0m: \033[32mload로 저장된 돈과 주가, 주식수를 불러올 수 있습니다\033[0m")
            print("\033[36mexit\033[0m: \033[32mexit로 게임을 종료 할 수 있습니다\033[0m")
            # print(f"{str(number_to_korean(balance))} {balance}")


        elif command.startswith("update"):
            try:
                # "update 10"과 같은 명령어에서 숫자 추출
                _, update_number = command.split()
                update_number = int(update_number)
            except (ValueError, IndexError):
                print("형식이 잘못되었습니다. 예: update 10")
                continue

            # 주가 업데이트 전 모든 주식의 가격을 저장해둠
            previous_prices = {eng_name: stock['price'] for eng_name, stock in stocks.items()}

            # 주가 업데이트
            for _ in range(update_number):
                update_stock_price()

            print("\n전체 업데이트 결과:")
            for eng_name, stock in stocks.items():
                old_price = previous_prices[eng_name]
                new_price = stock['price']
                percentage_change = ((new_price - old_price) / old_price) * 100

                # 색상 설정
                if percentage_change > 0:
                    color = '\033[91m'  # 빨간색
                elif percentage_change < 0:
                    color = '\033[94m'  # 파란색
                else:
                    color = '\033[0m'  # 기본 색상

                # 주가 정보 출력
                print(f"{stock['name']} 주가: {old_price}원 -> {new_price}원 ({color}{percentage_change:.2f}%\033[0m)")

        elif command == "save":
            save_game()

        elif command == "load":
            load_game()

        elif command == "exit":
            print("게임을 종료합니다.")
            break

        else:
            print("명령이 없습니다 새로 고침합니다")
            clear_screen()
            update_stock_price()
            display_status()

        # 매 라운드마다 주가 업데이트
        # update_stock_price()


if __name__ == "__main__":
    main()
