import unittest

from legalir_api.app import fuse, health, retrieve, root
from legalir_api.schemas import FuseRequest, RetrieveRequest


class ApiTests(unittest.TestCase):
    def test_root_redirects_to_docs(self):
        response = root()
        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], "/docs")

    def test_health(self):
        self.assertEqual(health()["status"], "ok")

    def test_retrieve(self):
        response = retrieve(
            RetrieveRequest(query="thủ tục thay đổi họ tên", top_k=3)
        )
        self.assertEqual(len(response.hits), 3)
        self.assertEqual(response.hits[0].document_id, "demo_002")

    def test_rrf_endpoint(self):
        response = fuse(
            FuseRequest(
                rankings=[["a", "b", "c"], ["b", "d", "a"]],
                weights=[1.0, 1.0], rrf_k=3, top_k=3,
            )
        )
        self.assertEqual(response.documents[0], "b")


if __name__ == "__main__":
    unittest.main()
