#!/usr/bin/env python3

import subprocess
from sys import platform
from os import path, mkdir
from configparser import ConfigParser
from datetime import datetime

DEFAULT_SECTION = "DEFAULT"

if platform == "win32":
    SYS_SECTION = "WIN32"
elif platform == "darwin":
    SYS_SECTION = "OSX"
else:
    SYS_SECTION = "LINUX"

CWD = path.dirname(path.realpath(__file__))

class Config:
    def __init__(self):
        self.config = ConfigParser()
        config_path = path.join(CWD, "sd.py.ini")
        if path.isfile(config_path):
            self.config.read(config_path)

    def get_optional_str(self, key: str) -> str | None:
        result = self.config.get(SYS_SECTION, key, fallback=None)
        if result is not None:
            return result.strip('"')
        else:
            return None

    def get_str(self, key: str, fallback: str) -> str:
        result = self.config.get(SYS_SECTION, key, fallback=None)
        if result is not None:
            return result.strip('"')
        else:
            return fallback

    def sd_img_out(self) -> str:
        return self.get_str("output_dir", "sd_img_out")

    def height(self) -> str:
        return self.get_str("height", "512")

    def width(self) -> str:
        return self.get_str("width", "512")

    def cfg_scale(self) -> str:
        return self.get_str("cfg-scale", "7.0")

    def strength(self) -> str:
        return self.get_str("strength", "0.9")

    def control_strength(self) -> str:
        return self.get_str("control-strength", "0.9")

    def sampling_method(self) -> str:
        return self.get_str("sampling-method", "euler_a")

    def steps(self) -> str:
        return self.get_str("steps", "30")

    def seed(self) -> str:
        return self.get_str("seed", "-1")

    def clip_skip(self) -> str:
        return self.get_str("clip-skip", "-1")

    def sd_bin(self) -> str:
        return self.get_str("sd_bin", "sd")

    def model(self) -> str | None:
        return self.get_optional_str("model")

    def lora_dir(self) -> str | None:
        return self.get_optional_str("lora_dir")

    def upscale_model(self) -> str | None:
        return self.get_optional_str("upscale-model")

    def vae(self) -> str | None:
        return self.get_optional_str("vae")

    def control_net(self) -> str | None:
        return self.get_optional_str("control-net")

    def batch_count(self) -> str | None:
        return self.get_optional_str("batch-count")

    def prompt(self) -> str:
        return self.get_str("prompt", "cute girl")

    def negative_prompt(self) -> str:
        return self.get_str("negative-prompt", "")


def main():
    config = Config()
    model = config.model()
    if model is None:
        print("Config is missing 'model' parameter")
        exit(1)

    model = path.realpath(model)
    if not path.isfile(model):
        print("%s: No such model is found" % model)
        exit(1)

    now = datetime.now()
    output_suffix = now.strftime("%d%m%y_%H%M%S_%f")
    output_path = path.join(CWD, config.sd_img_out())
    if not path.isdir(output_path):
        mkdir(output_path)
    output_path = path.join(output_path, output_suffix + ".png")

    sd_bin = config.sd_bin()
    run_cwd = path.dirname(sd_bin);

    args = [
        path.abspath(sd_bin),
        "--height", config.height(),
        "--width", config.width(),
        "--cfg-scale", config.cfg_scale(),
        "--strength", config.strength(),
        "--sampling-method", config.sampling_method(),
        "--steps", config.steps(),
        "--seed", config.seed(),
        "--clip-skip", config.clip_skip(),
        "--model", model,
        "--prompt", config.prompt(),
        "--negative-prompt", config.negative_prompt(),
        "--output", output_path,
    ]

    batch_count = config.batch_count();
    if batch_count is not None:
        args.append("--batch-count")
        args.append(batch_count)

    lora_dir = config.lora_dir();
    if lora_dir is not None:
        args.append("--lora-model-dir")
        args.append(lora_dir)

    upscale_model = config.upscale_model();
    if upscale_model is not None:
        args.append("--upscale-model")
        args.append(upscale_model)

    vae = config.vae();
    if vae is not None:
        args.append("--vae")
        args.append(vae)

    control_net = config.control_net();
    if control_net is not None:
        args.append("--control-net")
        args.append(control_net)
        args.append("--control-strength")
        args.append(config.control_strength())

    subprocess.run(args, shell=False, check=False, capture_output=False, cwd=run_cwd)

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(error)
