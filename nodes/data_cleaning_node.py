import json

async def main(args: Args) -> Output:
    Product_category = ""
    ASR = ""
    OCR = ""
    Product_image = ""
    URL_Frames = "[]"

    try:
        def to_text(data):
            if isinstance(data, str):
                return data.strip()
            elif isinstance(data, (dict, list)):
                try:
                    return json.dumps(data, ensure_ascii=False)
                except Exception:
                    return str(data)
            else:
                return str(data)

        params = args.params
        input_raw = params.get('input', {})

        if isinstance(input_raw, str):
            try:
                input_data = json.loads(input_raw)
            except json.JSONDecodeError as e:
                raise ValueError(f"input解析失败：{repr(e)}")
        elif isinstance(input_raw, dict):
            input_data = input_raw
        else:
            raise ValueError(f"不支持的input类型：{type(input_raw)}")

        if 'output' in input_data:
            output_node = input_data['output']
        else:
            output_node = input_data

        if 'result' not in output_node:
            raise ValueError(f"output节点中没有找到result字段")
        result_node = output_node['result']

        asr_node = result_node.get('VideoMachineCheckInfo.asr', {})
        ASR = asr_node.get('feature_value', '').strip()

        ocr_node = result_node.get('VideoMachineCheckInfo.merge_ocr', {})
        OCR = ocr_node.get('feature_value', '').strip()

        product_list_node = result_node.get('VideoMachineCheckInfo.product_list', {})
        product_list_raw = product_list_node.get('feature_value', '')
        if product_list_raw:
            try:
                product_list_data = json.loads(product_list_raw)
                if isinstance(product_list_data, list) and len(product_list_data) > 0:
                    first_product = product_list_data[0]
                    if isinstance(first_product, dict):
                        Product_category = first_product.get('category', '')
            except Exception as e:
                print(f"商品类目解析失败：{repr(e)}")

        product_images_node = result_node.get('VideoMachineCheckInfo.product_images', {})
        product_images_raw = product_images_node.get('feature_value', '')
        if product_images_raw:
            try:
                product_images_array = json.loads(product_images_raw)
                if isinstance(product_images_array, list) and len(product_images_array) > 0:
                    inner_array = product_images_array[0]
                    if isinstance(inner_array, list) and len(inner_array) > 0:
                        Product_image = inner_array[0].strip()
            except Exception as e:
                print(f"商品主图解析失败：{repr(e)}")

        video_slice_node = result_node.get('VideoMachineCheckInfo.video_slice_list', {})
        video_slice_raw = video_slice_node.get('feature_value', '')
        if video_slice_raw:
            try:
                video_slice_array = json.loads(video_slice_raw)
                if isinstance(video_slice_array, list):
                    clean_urls = [url.strip() for url in video_slice_array if isinstance(url, str) and url.strip()]
                    if len(clean_urls) <= 5:
                        sampled = clean_urls
                    else:
                        step = len(clean_urls) / 5
                        sampled = [clean_urls[int(i * step)] for i in range(5)]
                    URL_Frames = json.dumps(sampled, ensure_ascii=False)
            except Exception as e:
                print(f"视频帧解析失败：{repr(e)}")

    except Exception as e:
        print(f"全局异常：{repr(e)}")

    ret: Output = {
        "Product_category": Product_category,
        "ASR": ASR,
        "OCR": OCR,
        "Product_image": Product_image,
        "URL_Frames": URL_Frames
    }
    return ret
