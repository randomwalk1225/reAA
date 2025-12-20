# patch_dpb.py
data = open("PROJECT.bin", "rb").read()
patched = data.replace(b"DPB=", b"DPx=")
open("PROJECT_patched.bin", "wb").write(patched)
print("패치 완료: PROJECT_patched.bin 생성됨")
