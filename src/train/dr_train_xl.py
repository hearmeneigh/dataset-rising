from train.vendor.huggingface.diffusers.train_text_to_image_sdxl import main as vendor_main, parse_args


def main():
    vendor_main(args=parse_args())


if __name__ == "__main__":
    main()
