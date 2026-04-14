import sys
print('Python路径:', sys.path)
try:
    import generator
    print('成功导入generator模块')
    print('generator模块路径:', generator.__file__)
except Exception as e:
    print('导入失败:', e)
