import sys
import json

from osh.parsing import parse, dump


def main():
    cmd = sys.argv[1]
    print(json.dumps(dump(*parse(cmd))))


if __name__ == "__main__":
    main()
