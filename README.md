# Tcp

完美改成 **你喜欢的【变量 + if 判断】模式**，格式、风格、逻辑全部对齐你的写法，**直接复制就能用**。

# 改风格后的最终命令
```bash
keep1="yy258224_tt22041854"
keep2="yy58193_tt11057302"

for dir in */; do
    d="${dir%/}"
    if [ "$d" != "$keep1" ] && [ "$d" != "$keep2" ]; then
        echo "删除文件夹: $d"
        rm -rf "$d"
    fi
done
```

# 先预览不删除（安全版）
```bash
keep1="yy258224_tt22041854"
keep2="yy258193_tt11057302"

for dir in */; do
    d="${dir%/}"
    if [ "$d" != "$keep1" ] && [ "$d" != "$keep2" ]; then
        echo "将要删除: $d"
    else
        echo "保留: $d"
    fi
done
```

---

## 完全匹配模式特点
- 顶部定义 `keep1`、`keep2` 变量
- 遍历目录并去掉末尾 `/` → `d="${dir%/}"`
- 使用 `if [ ] && [ ]` 判断
- 带 `echo` 提示删除内容
- 格式整齐、易读、易修改
- 最安全、最专业

