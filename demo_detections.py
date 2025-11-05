"""Demo: Show what the Purple Agent can and cannot detect."""
import asyncio
import httpx

async def test_detections():
    samples = [
        {"name": "F-string interpolation", "code": 'query = f"SELECT * FROM users WHERE id={user_id}"', "expected": "DETECT"},
        {"name": "String concatenation", "code": 'query = "SELECT * FROM users WHERE id=" + str(user_id)', "expected": "DETECT"},
        {"name": "% formatting", "code": 'query = "SELECT * FROM users WHERE id=%s" % user_id', "expected": "DETECT"},
        {"name": "Parameterized query", "code": 'cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))', "expected": "SAFE"},
        {"name": "ORM usage", "code": 'User.objects.filter(id=user_id)', "expected": "SAFE"},
    ]
    print("\n" + "="*70)
    print("🔍 Purple Agent Detection Capabilities Demo")
    print("="*70 + "\n")
    async with httpx.AsyncClient(timeout=5.0) as client:
        for i, sample in enumerate(samples, 1):
            try:
                response = await client.post("http://127.0.0.1:8000/detect",
                    json={"test_case_id": f"demo_{i}", "code": sample["code"], "language": "python", "category": "classic_sqli"})
                result = response.json()
                is_vuln = result["is_vulnerable"]
                confidence = result["confidence"]
                status = "✅" if ((sample["expected"] == "DETECT" and is_vuln) or (sample["expected"] == "SAFE" and not is_vuln)) else "❌"
                verdict = "VULNERABLE" if is_vuln else "SAFE      "
                print(f"{status} {i}. {sample['name']:30s}")
                print(f"   Expected: {sample['expected']:10s} | Got: {verdict} | Confidence: {confidence:.2f}")
                print(f"   Code: {sample['code'][:60]}...")
                print()
            except Exception as e:
                print(f"❌ {i}. ERROR: {e}\n")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_detections())
