import os
import json

def element_routine(elem):
    if isinstance(elem["value"], list):
        finish = False
        while not finish:
            print("For item:", elem["name"])
            for ind, d in enumerate(elem["value"]):
                print(ind, "--", d)
            print("Please input the left number in the list:")
            input_string = input()
            try:
                num = int(input_string)
                assert num >= 0 and num <= len(elem["value"]) - 1
            except Exception:
                print("Input number is invalid. Please try again.")
                finish = False
            else:
                finish = True
        return elem["value"][num]

    elif isinstance(elem["value"], str):
        finish = False
        while not finish:
            print("For item:", elem["name"])
            print("Please input a number in the range:", elem["value"])
            input_string = input()
            try:
                num = float(input_string)
            except Exception:
                print("Input number is invalid. Please try again.")
                finish = False
            else:
                finish = True
        return num

    else:
        print("Unsupported type:", type(elem["value"]))
        return False


def terminal_session(save_dir, metafile, savefile="meta.json"):
    assert os.path.exists(metafile)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    fp = open(metafile, "r")
    meta = json.load(fp)
    fp.close()
    assert isinstance(meta, list)
    print("Use device file:", os.path.basename(metafile))

    sorted(meta, key=lambda m: m["index"], reverse=False)

    print("----start inputting meta-data----")

    save_content = []
    for elem in meta:
        assert isinstance(elem, dict)
        val = element_routine(elem)
        save_content.append({"name" : elem["name"], "value" : val})

    filepath = os.path.join(save_dir, savefile)
    fp = open(filepath, "w")
    json.dump(save_content, fp, indent=4)
    fp.close()

    print("----end inputting meta-data----")
    print("Write meta-data to", filepath)
    return

if __name__ == "__main__":
    terminal_session(".", "tgp110.json")