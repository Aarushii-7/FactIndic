import json
import urllib.request
import time

TEST_SAMPLES = [
    # Hindi 1: News / Science
    {
        "id": "HI-01",
        "category": "News Report (Science & Tech)",
        "language": "hindi",
        "source": "भारतीय अंतरिक्ष अनुसंधान संगठन (ISRO) ने श्रीहरिकोटा के सतीश धवन अंतरिक्ष केंद्र से एक नया संचार उपग्रह सफलतापूर्वक लॉन्च किया। वैज्ञानिकों ने इस मिशन को ऐतिहासिक सफलता बताया। यह उपग्रह अगले 10 वर्षों तक देश के दूरदराज के क्षेत्रों में हाई-स्पीड इंटरनेट और दूरसंचार सेवाएं प्रदान करेगा।"
    },
    # Hindi 2: Numerical & Announcement
    {
        "id": "HI-02",
        "category": "Government & Numerical Announcement",
        "language": "hindi",
        "source": "वित्त मंत्रालय ने शुक्रवार को घोषणा की कि वित्त वर्ष 2024-25 में कुल सकल GST संग्रह ₹20.18 लाख करोड़ तक पहुंच गया, जो पिछले वर्ष के ₹18.10 लाख करोड़ से 11.5 प्रतिशत अधिक है। हालांकि, अंतिम लेखापरीक्षित आंकड़े 31 मार्च के बाद जारी किए जाएंगे।"
    },
    # Hindi 3: Health Advisory / Uncertainty
    {
        "id": "HI-03",
        "category": "Health Advisory (Uncertainty & Attribution)",
        "language": "hindi",
        "source": "स्वास्थ्य विभाग ने चेतावनी दी है कि सर्दियों के दौरान मौसमी इन्फ्लूएंजा के मामलों में वृद्धि होने की संभावना है, हालांकि किसी नए घातक वेरिएंट की पुष्टि नहीं हुई है। अधिकारियों ने वरिष्ठ नागरिकों को सावधानी बरतने और भीड़भाड़ में मास्क पहनने की सलाह दी है, परंतु किसी प्रकार का लॉकडाउन या यात्रा प्रतिबंध लागू नहीं किया गया है।"
    },
    # Hinglish 1: Dialogue & Directionality
    {
        "id": "HG-01",
        "category": "Dialogue (Speaker/Listener Directionality)",
        "language": "hinglish",
        "source": "Aarav: Maine Rishabh ko kal subah school jane ke liye bola tha. Sneha: Acha, to wo gaya kya? Aarav: Nahi, usne bola ki kal Math ka test nahi hai isliye wo nahi jayega."
    },
    # Hinglish 2: Announcement & Negation
    {
        "id": "HG-02",
        "category": "Dialogue (Negation & Venue Change)",
        "language": "hinglish",
        "source": "Karan: Guys kal subah 10 baje college auditorium mein placement talk hai. Simran: Par sunne mein aaya tha ki placement drive cancel ho gaya hai? Karan: Nahi, drive cancel nahi hua hai, bas venue change ho gaya hai pehle seminar hall tha ab auditorium hai."
    },
    # Hinglish 3: Intention vs Outcome
    {
        "id": "HG-03",
        "category": "Code-Mixed Academic (Intention vs. Outcome)",
        "language": "hinglish",
        "source": "Many students apna daily study schedule plan karte hain taaki important assignment deadlines miss na ho. Lekin classes aur projects ke beech time manage karna kaafi challenging hota hai."
    },
    # English 1: Monetary Policy / Numbers
    {
        "id": "EN-01",
        "category": "Economic Report (Numerical Data)",
        "language": "english",
        "source": "The Reserve Bank of India on Friday kept the benchmark repo rate unchanged at 6.5 percent for the eighth consecutive monetary policy review. Governor Shaktikanta Das stated that while headline inflation has moderated to 4.8 percent, food price volatility remains a significant risk."
    },
    # English 2: Corporate Investment / Uncertainty
    {
        "id": "EN-02",
        "category": "Corporate Announcement (Timeline & Conditions)",
        "language": "english",
        "source": "NexTech Corporation announced plans to invest $450 million in a new semiconductor design facility in Bengaluru, subject to central government subsidies. The management clarified that while land acquisition is complete, commercial production will not commence before early 2027."
    },
    # English 3: Medical Discovery / Preliminary Findings
    {
        "id": "EN-03",
        "category": "Scientific Research (Uncertainty & Caution)",
        "language": "english",
        "source": "Medical researchers at Oxford University have identified a blood biomarker that may detect early signs of Parkinson's disease up to seven years before clinical symptoms emerge. However, the study authors emphasized that the findings are preliminary and require validation across larger, diverse patient cohorts before clinical deployment."
    }
]

def run_tests():
    url = "http://localhost:8000/api/summarize_all"
    results = []

    print(f"Executing Controlled A/B Evaluation across {len(TEST_SAMPLES)} test cases...\n")

    for i, s in enumerate(TEST_SAMPLES, 1):
        print(f"[{i}/{len(TEST_SAMPLES)}] Testing {s['id']} ({s['category']})...")
        payload = json.dumps({
            "source_text": s["source"],
            "language": s["language"],
            "summary_length": "medium"
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                elapsed = round(time.time() - t0, 2)
                res_entry = {
                    "id": s["id"],
                    "category": s["category"],
                    "language": s["language"],
                    "source": s["source"],
                    "elapsed_total": elapsed,
                    "condition_A": data["condition_A"],
                    "condition_B": data["condition_B"],
                    "condition_C": data["condition_C"],
                }
                results.append(res_entry)
                print(f"    Done in {elapsed}s | A Supp: {data['condition_A']['support_rate']}% | B Supp: {data['condition_B']['support_rate']}% | C Supp: {data['condition_C']['support_rate']}%")
        except Exception as e:
            print(f"    Error on {s['id']}: {e}")

    with open("/Users/aarushi/factIndic/ab_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\nAll tests completed! Results saved to /Users/aarushi/factIndic/ab_test_results.json")

if __name__ == "__main__":
    run_tests()
