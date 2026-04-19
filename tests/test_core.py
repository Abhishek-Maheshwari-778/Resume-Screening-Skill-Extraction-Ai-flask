from src.extractor import extract_skills, extract_name, extract_email

def test_skill_extraction():
    text = "Experienced software engineer with skills in Python, Java, and Machine Learning."
    skills = extract_skills(text)
    assert "python" in skills
    assert "java" in skills
    assert "machine learning" in skills
    print("✓ Skill extraction test passed!")

def test_name_extraction():
    text = "Abhishek Maheshwari\nAddress: 123 Street\nEmail: abhi@test.com"
    name = extract_name(text)
    assert "Abhishek" in name
    print("✓ Name extraction test passed!")

def test_email_extraction():
    text = "Contact me at john.doe@example.org for inquiries."
    email = extract_email(text)
    assert email == "john.doe@example.org"
    print("✓ Email extraction test passed!")

if __name__ == "__main__":
    print("Running Project Tests...")
    test_skill_extraction()
    test_name_extraction()
    test_email_extraction()
    print("All tests passed successfully!")
