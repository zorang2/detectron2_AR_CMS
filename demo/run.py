'''
12.07 / argparse 실습을 위한 파일입니다.
'''

import argparse

parser = argparse.ArgumentParser()

parser.add_argument("square", type=int, help = "display a square of a given number")
parser.add_argument("-v", "--verbosity", action="count", help="increase output verbosity")

args = parser.parse_args()
answer = args.square**2

if args.verbosity == 2:
    print("the square of {} equals {}".format(args.square, answer))
elif args.verbosity == 1:
    print("{}^2 == {}".format(args.square, answer))
else:
    print(answer)

# print(args.square**2)





'''
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--decimal", dest="decimal", action="store") # extra value
parser.add_argument("-f", "--fast", dest="fast", action="store_true") # existence/nonexistence
args = parser.parse_args()


print(args)
print(args.decimal)
print(args.fast)

'''

'''
# 인자 값을 받을 수 있는 인스턴스 생성
parser = argparse.ArgumentParser(description='조랭근 argparse 테스트입니다.')

# 입력받을 인자값 등록
parser.add_argument('-t', '--target', required=True, help='어느 것을 요구하냐')
parser.add_argument('-e', '--env', required=False, default='dev', help='실행 환경은 뭐냐')

# 입력받은 인자값을 args에 저장 (type : namespace)
args = parser.parse_args()

# 입력받은 인자값 출력
print(args.target)
print(args.env)
'''
