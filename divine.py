import argparse
import logging
from FileManager import FileManager

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--number", required=True, type=int, action='append', help="Episode index to be moved")
parser.add_argument(      "--logging",               type=str, help="Verbose"                  , default="info")
(args,unknown_args) = parser.parse_known_args()

def get_gua(num_down, num_up, num_change):
    # 八卦对应表
    gua_map = {
        1: "乾（天）", 2: "兑（泽）", 3: "离（火）", 4: "震（雷）",
        5: "巽（风）", 6: "坎（水）", 7: "艮（山）", 8: "坤（地）"
    }

    try:
        # 计算余数
        # 如果整除（余数为0），则取8或6
        res_down = num_down % 8 or 8
        res_up = num_up % 8 or 8
        res_change = num_change % 6 or 6

        print("\n--- 占卜结果 ---")
        print(f"上卦为：{gua_map[res_up]}")
        print(f"下卦为：{gua_map[res_down]}")
        print(f"本卦为：【{gua_map[res_up][0]}{gua_map[res_down][0]}】卦")
        print(f"动爻为：第 {res_change} 爻")
        print("---------------")
        print("💡 建议：请根据本卦的爻辞和动爻的变动进行推解。")

    except ValueError:
        print("错误：请输入有效的整数数字。")

if __name__ == "__main__":
    get_gua(args.number[0], args.number[1], args.number[2])