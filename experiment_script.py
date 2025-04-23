import os
import shlex
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


def run_single_test(content_path, style_image, test_mode, results_root):
    """执行单个测试任务"""
    content_name = content_path.name
    style_name = style_image.stem
    experiment_name = f"{content_name}_{test_mode}_{style_name}"

    output_dir = results_root / experiment_name
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "python", "test.py",
        '--name', "mmis_sunny2diffweathers",
        "--task", "MMIS",
        "--gpu_ids", 0,
        "--checkpoints_dir", "./checkpoints",
        "--batchSize", 1,
        "--dataset_mode", "sunny2diffweathers",
        "--croot", "./datasets/bdd100k",
        "--sroot", "./datasets/bdd100k",
        "--nThreads", 4,
        "--no_pairing_check",
        "--no_instance",
        "--num_upsampling_layers", "more",
        "--alpha", 1.0,
        "--results_dir", str(output_dir.resolve()),
        "--which_epoch", "latest",
        "--show_input",
        "--test_mode", test_mode,
        "--s_image", str(style_image.resolve()),
        "--c_path", str(content_path.resolve())
    ]

    log_file = output_dir / "test_log.txt"
    with open(log_file, "w") as f:
        # 记录完整命令和参数（新增部分）
        f.write(f"========== 测试参数 ==========\n")
        f.write(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"执行命令: {cmd}\n")  # 👈 记录完整命令行
        f.write(f"内容路径: {content_path}\n")
        f.write(f"风格图片: {style_image}\n")
        f.write(f"测试模式: {test_mode}\n")
        f.write(f"===============================\n\n")
        # 将所有参数转换为字符串
        cmd_str = [str(item) for item in cmd]
        result = subprocess.run(cmd_str,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                check=True,
                                encoding='utf-8',
                                cwd=os.path.dirname(os.path.abspath("test.py")))

        # 记录输出
        f.write("STDOUT:\n")
        f.write(result.stdout)
        f.write("\nSTDERR:\n")
        f.write(result.stderr)

        # 检查是否有错误
        if result.returncode != 0:
            f.write(f"\n命令执行失败，返回码: {result.returncode}\n")
            print(f"命令执行失败，详情请查看日志文件: {log_file}")
        else:
            f.write("\n命令执行成功\n")
            print(f"命令执行成功，详情请查看日志文件: {log_file}")

    return experiment_name


def main(test_dir, reference_dir, results_root="auto_results", max_workers=1):
    results_root = Path(results_root)
    test_folders = [f for f in Path(test_dir).iterdir() if f.is_dir()]
    style_groups = []

    # 收集所有测试任务
    for style_dir in Path(reference_dir).iterdir():
        if not style_dir.is_dir():
            continue
        test_mode = style_dir.name
        for img in style_dir.glob("*"):
            if img.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                style_groups.append((style_dir, img, test_mode))

    # 生成任务参数
    tasks = []
    for content_path in test_folders:
        for style_dir, style_img, test_mode in style_groups:
            tasks.append((
                content_path,
                style_img,
                test_mode
            ))


    # 使用单个进度条（移除并行逻辑）
    with tqdm(total=len(tasks), desc="测试进度", unit="task") as pbar:
        for task_args in tasks:
            try:
                # 直接调用执行函数
                exp_name = run_single_test(*task_args, results_root)
                pbar.set_postfix(current=exp_name)  # 显示当前任务名称
            except Exception as e:
                tqdm.write(f"任务失败: {str(e)}")
            finally:
                pbar.update(1)  # 确保进度条始终更新

    print(f"所有测试完成，结果保存在：{results_root}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_dir", type=str, help="包含测试内容文件夹的根目录")
    parser.add_argument("--reference_dir", type=str, help="包含参考风格的根目录")
    parser.add_argument("--results_root", type=str, default="auto_results",
                        help="结果保存根目录")
    args = parser.parse_args()

    main(
        test_dir=args.test_dir,
        reference_dir=args.reference_dir,
        results_root=args.results_root,
        max_workers=args.max_workers
    )