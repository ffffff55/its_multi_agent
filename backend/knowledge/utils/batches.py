"""按批遍历，调用方负责每一批都写完再返回。"""


def iter_batches(items: list, batch_size: int):
    if batch_size <= 0:
        raise ValueError("batch_size 必须大于 0")
    for start in range(0, len(items), batch_size):
        yield items[start:start + batch_size]
