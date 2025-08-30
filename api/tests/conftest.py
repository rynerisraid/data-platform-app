import pytest
from fastapi.testclient import TestClient
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c