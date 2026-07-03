# Copyright (c) 2026 MyCompany LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from typing import List, Dict, Any

class NewsCollector:
    """Mock News Collector stage.
    
    Fetches raw news articles containing titles, contents, source URLs, and syllabus tags.
    """
    def __init__(self):
        # A list of mock news articles for testing
        self.mock_db = [
            # PSC items
            {
                "title": "Supreme Court Rules on Center-State Financial Devolution",
                "content": "In a landmark judgment, the Supreme Court clarified the constitutional boundaries of financial devolution between the Central Government and State Governments, highlighting the essence of fiscal federalism.",
                "url": "https://example.com/sc-federalism-devolution",
                "tags": ["Constitution", "Federalism", "State Policy"]
            },
            {
                "title": "State Government Announces Administrative Reforms Commission",
                "content": "To streamline public service delivery, a new Administrative Reforms Commission has been formed to recommend governance measures and restructuring of civil services.",
                "url": "https://example.com/admin-reforms-commission",
                "tags": ["Public Administration", "Governance"]
            },
            {
                "title": "Amendment to Civil Services Conduct Rules Proposed",
                "content": "The government has proposed an amendment to the civil services conduct rules to improve digital transparency and public administration efficiency.",
                "url": "https://example.com/civil-services-rules",
                "tags": ["Constitution", "Public Administration"]
            },
            {
                "title": "Inter-State Council Meets to Discuss Border Infrastructure",
                "content": "The Inter-State Council convened to discuss coordinating infrastructure developments and security policies across borders, cementing cooperative federalism principles.",
                "url": "https://example.com/inter-state-council-meet",
                "tags": ["Federalism", "Governance"]
            },
            
            # SSC items
            {
                "title": "Archaeologists Discover Indus Valley Site in Western India",
                "content": "A team of researchers discovered a new Harappan-era settlement with advanced water harvesting systems, contributing to historical knowledge of the Indus Valley Civilization.",
                "url": "https://example.com/indus-valley-discovery",
                "tags": ["History", "Geography"]
            },
            {
                "title": "Annual Monsoon Performance Report Released",
                "content": "The meteorological department released its reports on spatial distribution of monsoon rainfall, indicating changes in geographic patterns and agrarian impacts.",
                "url": "https://example.com/monsoon-geography-report",
                "tags": ["Geography", "General Science"]
            },
            {
                "title": "Global Innovation Index 2026: India Ranks 38th",
                "content": "India has climbed to the 38th position in the Global Innovation Index, led by strong performance in general science education and digital services export.",
                "url": "https://example.com/global-innovation-index",
                "tags": ["General Science", "Polity"]
            },
            {
                "title": "New Bill on Electoral Integrity Tabled in Parliament",
                "content": "Parliament initiated discussions on a new electoral reform bill aimed at reducing proxy voting and enhancing democratic representation.",
                "url": "https://example.com/electoral-bill-parliament",
                "tags": ["Polity", "History"]
            },
            
            # Railway items
            {
                "title": "Indian Railways Completes 100% Electrification of Golden Quadrilateral",
                "content": "The Ministry of Railways announced the complete electrification of the Golden Quadrilateral routes, marking a massive milestone in railway history and transportation efficiency.",
                "url": "https://example.com/railway-electrification-complete",
                "tags": ["Railway History", "Transportation"]
            },
            {
                "title": "Bullet Train Project Trial Run Scheduled for Late 2026",
                "content": "The first high-speed rail corridor trials are scheduled, bringing state-of-the-art Japanese Shinkansen technology to the country's transport system.",
                "url": "https://example.com/bullet-train-trial-run",
                "tags": ["Transportation", "General Awareness"]
            },
            {
                "title": "Vande Bharat Sleeper Coach Prototype Unveiled",
                "content": "The government unveiled the prototype for Vande Bharat sleeper trains designed for overnight long-distance travel, elevating passenger comfort and rail technology.",
                "url": "https://example.com/vande-bharat-sleeper-prototype",
                "tags": ["Transportation", "Railway History"]
            },
            {
                "title": "ISRO Partners with Indian Railways for Real-Time Train Tracking",
                "content": "ISRO satellite telemetry will now power real-time train tracking and automatic signaling, showcasing a strong integration of general science with transport management.",
                "url": "https://example.com/isro-railway-tracking",
                "tags": ["General Science", "Transportation", "General Awareness"]
            },
            
            # Additional items that overlap/extra
            {
                "title": "National Science Day Focuses on Indigenous Technologies",
                "content": "This year's theme for National Science Day is 'Indigenous Technologies for Viksit Bharat', highlighting achievements in space exploration and green energy.",
                "url": "https://example.com/national-science-day",
                "tags": ["General Science", "General Awareness"]
            },
            {
                "title": "New Green Hydrogen Plant Inaugurated in Gujarat",
                "content": "The country's largest green hydrogen production facility was inaugurated to power logistics and heavy transport, supporting ecological goals.",
                "url": "https://example.com/green-hydrogen-plant",
                "tags": ["General Science", "Transportation"]
            },
            {
                "title": "Government Launches Digital Library for Ancient Indian Manuscripts",
                "content": "A new cloud-based digital portal has launched, housing high-resolution scans of over 50,000 ancient manuscripts, promoting historical research.",
                "url": "https://example.com/ancient-manuscripts-portal",
                "tags": ["History", "General Awareness"]
            }
        ]

    def collect(self, exam_type: str) -> List[Dict[str, Any]]:
        """Simulates news retrieval for the specified exam category.
        
        Returns all mock articles.
        """
        print(f"[NewsCollector] Collecting articles for exam type: {exam_type}")
        return self.mock_db
