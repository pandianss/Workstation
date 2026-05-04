import os

def check_fonts():
    d = 'data/fonts'
    if not os.path.exists(d):
        print(f"Directory {d} does not exist.")
        return
        
    for f in os.listdir(d):
        p = os.path.join(d, f)
        if os.path.isfile(p):
            with open(p, 'rb') as fd:
                head = fd.read(16)
                print(f"{f}: {head}")

if __name__ == "__main__":
    check_fonts()
