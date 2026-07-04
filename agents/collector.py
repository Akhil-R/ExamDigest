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
            # PSC (including Kerala Specific) items
            {
                "title": "Vizhinjam International Seaport Commissions Phase-1 Operations",
                "content": "India's first deepwater transshipment port at Vizhinjam, Kerala, has officially commenced commercial operations. Managed by Adani Ports in partnership with the Government of Kerala, the port has successfully received its first mothership, positioning India as a global maritime hub.",
                "url": "https://kerala.gov.in/press-release/vizhinjam-seaport-phase1",
                "tags": ["State Infrastructure", "Kerala Governance", "Transportation"]
            },
            {
                "title": "Kerala Fiber Optic Network (KFON) Launches Phase-2 Expansion",
                "content": "The Kerala Government has launched the second phase of KFON, aiming to extend free high-speed internet connectivity to an additional 20,000 below-poverty-line (BPL) families and over 5,000 government offices across rural districts, promoting digital inclusion.",
                "url": "https://kerala.gov.in/press-release/kfon-phase2-expansion",
                "tags": ["Kerala Governance", "State Schemes", "State Infrastructure"]
            },
            {
                "title": "Kerala's K-Smart Application Launched for Unified Local Body Services",
                "content": "The Local Self Government Department of Kerala has introduced K-Smart (Kerala Solution for Managing Administrative Reformation and Transformation) to digitize all services across local bodies, including birth certificates, building permits, and trade licenses, onto a single app.",
                "url": "https://kerala.gov.in/press-release/ksmart-local-bodies",
                "tags": ["Kerala Governance", "State Schemes", "Governance"]
            },
            {
                "title": "India's First Digital Science Park Commences in Trivandrum",
                "content": "The foundation stone was laid for India's first Digital Science Park in Thiruvananthapuram, Kerala. The project focuses on research and industry-academy collaboration in artificial intelligence, robotics, cybersecurity, and smart hardware.",
                "url": "https://kerala.gov.in/press-release/trivandrum-digital-science-park",
                "tags": ["Kerala Governance", "Literacy & Education", "State Infrastructure"]
            },
            {
                "title": "Kerala Literacy Mission Announces 'Aksharasree' Program Expansion",
                "content": "The State Literacy Mission Authority has extended its 'Aksharasree' continuing education project to tribal colonies and remote coastal areas, offering equivalency courses up to the higher secondary level for adults.",
                "url": "https://kerala.gov.in/press-release/aksharasree-literacy-mission",
                "tags": ["Kerala Governance", "Literacy & Education", "State Schemes"]
            },
            {
                "title": "Kudumbashree Enterprise Launches Haritha Karma Sena Waste Units",
                "content": "Kerala's Kudumbashree network has partnered with local panchayats to scale Haritha Karma Sena units. The initiative provides green employment to women while implementing scientific solid-waste management and recycling protocols state-wide.",
                "url": "https://kerala.gov.in/press-release/kudumbashree-haritha-karma-sena",
                "tags": ["Kerala Governance", "State Schemes", "Governance"]
            },
            {
                "title": "Supreme Court Rules on Center-State Financial Devolution",
                "content": "In a landmark judgment, the Supreme Court clarified the constitutional boundaries of financial devolution between the Central Government and State Governments, highlighting the essence of fiscal federalism under Article 280.",
                "url": "https://pib.gov.in/press-release/sc-financial-devolution-judgment",
                "tags": ["Constitution", "Federalism", "State Policy"]
            },
            {
                "title": "State Government Announces Administrative Reforms Commission",
                "content": "To streamline public service delivery, a new Administrative Reforms Commission has been formed by the state government to recommend governance measures and restructuring of civil services to reduce red tape.",
                "url": "https://kerala.gov.in/press-release/administrative-reforms-commission",
                "tags": ["Public Administration", "Governance"]
            },
            
            # SSC (Indian National Current Affairs, History, Polity, Geography) items
            {
                "title": "ISRO Gaganyaan Crew Module Escape System Test Successful",
                "content": "The Indian Space Research Organisation (ISRO) successfully conducted the Test Vehicle Abort Mission (TV-D1) for the Gaganyaan project, demonstrating the crew module's escape system capabilities under high-altitude abort conditions.",
                "url": "https://isro.gov.in/press-release/gaganyaan-tv-d1-success",
                "tags": ["General Science", "National Initiatives", "Polity"]
            },
            {
                "title": "India Semiconductor Mission: Micron's First Fab Plant Tabled in Gujarat",
                "content": "Under the India Semiconductor Mission (ISM), construction of the country's first commercial semiconductor assembly and test facility has commenced in Sanand, Gujarat, boosting domestic electronics manufacturing and economy.",
                "url": "https://pib.gov.in/press-release/semiconductor-mission-sanand-fab",
                "tags": ["Economy", "National Initiatives", "General Science"]
            },
            {
                "title": "Union Cabinet Approves Unified Pension Scheme (UPS)",
                "content": "The Union Cabinet has approved the Unified Pension Scheme (UPS) for central government employees. It guarantees 50% of the average basic pay drawn in the last 12 months before retirement as a pension, combining features of NPS and OPS.",
                "url": "https://pib.gov.in/press-release/unified-pension-scheme-approved",
                "tags": ["Polity", "National Initiatives", "Economy"]
            },
            {
                "title": "Electoral Integrity Reform Bill Tabled in Lok Sabha",
                "content": "A new Electoral Integrity Reform Bill has been introduced in Parliament, proposing linking of voter IDs with Aadhaar on a voluntary basis, and implementing a single voter list for local, state, and parliamentary elections.",
                "url": "https://pib.gov.in/press-release/electoral-integrity-bill-parliament",
                "tags": ["Polity", "Constitution", "History"]
            },
            {
                "title": "Archaeologists Discover Harappan-Era Water Systems in Rakhigarhi",
                "content": "Excavations at the Harappan site of Rakhigarhi in Haryana have uncovered an intricate network of burnt-brick drainage channels and terracotta water pipes, indicating sophisticated city planning during the Indus Valley Civilization.",
                "url": "https://pib.gov.in/press-release/rakhigarhi-harappan-drainage-find",
                "tags": ["History", "Geography"]
            },
            {
                "title": "IMD Releases Report on Monsoon Patterns Over Western Ghats",
                "content": "The India Meteorological Department (IMD) published a decadal study revealing shifting precipitation zones and increased instances of extreme rainfall events over the micro-regions of the Western Ghats mountain range.",
                "url": "https://pib.gov.in/press-release/imd-monsoon-western-ghats-report",
                "tags": ["Geography", "General Science"]
            },
            
            # Railway (Transportation, Railway History, Tech) items
            {
                "title": "Indian Railways Achieves 100% Electrification of Golden Quadrilateral",
                "content": "The Ministry of Railways announced the complete electrification of the Golden Quadrilateral routes (connecting Delhi, Mumbai, Chennai, and Kolkata), achieving a reduction in carbon emissions and fuel costs.",
                "url": "https://pib.gov.in/press-release/railway-golden-quadrilateral-electrification",
                "tags": ["Railway History", "Transportation", "Infrastructure & Technology"]
            },
            {
                "title": "Vande Bharat Sleeper Coach Prototype Unveiled by BEML",
                "content": "The prototype of the much-awaited Vande Bharat Sleeper train was unveiled in Bengaluru. Designed by BEML, the train is built for long-distance overnight travel with crashworthy designs and advanced passenger comfort features.",
                "url": "https://pib.gov.in/press-release/vande-bharat-sleeper-prototype-unveiled",
                "tags": ["Transportation", "Infrastructure & Technology", "General Awareness"]
            },
            {
                "title": "Kavach 4.0 Automatic Train Protection Deployed on High-Density Routes",
                "content": "Indian Railways has commenced the field deployment of Kavach 4.0, its indigenous Automatic Train Protection (ATP) system. The system automatically applies brakes if the driver fails to react, preventing head-on collisions.",
                "url": "https://pib.gov.in/press-release/kavach-train-protection-deployment",
                "tags": ["Transportation", "Infrastructure & Technology", "General Science"]
            },
            {
                "title": "India's First Hydrogen-Powered Train Trial Scheduled on Jind-Sonipat Route",
                "content": "The Northern Railway zone is set to conduct trials of India's first hydrogen fuel cell-powered passenger train on the Jind-Sonipat section in Haryana, promoting zero-emission green transportation.",
                "url": "https://pib.gov.in/press-release/hydrogen-train-trials-jind-sonipat",
                "tags": ["Transportation", "Infrastructure & Technology", "General Science"]
            },
            {
                "title": "Historic Nilgiri Mountain Railway Inducts Custom Steam Locomotive",
                "content": "The Golden Rock Workshop of Southern Railway has manufactured and delivered a new coal-fired steam locomotive engine to the Nilgiri Mountain Railway (NMR), preserving the heritage status of this UNESCO World Heritage Site.",
                "url": "https://pib.gov.in/press-release/nilgiri-mountain-railway-steam-loco",
                "tags": ["Railway History", "Transportation"]
            },
            {
                "title": "ISRO and Indian Railways Partner for Real-Time Satellite Tracking",
                "content": "Real-time train information system (RTIS) devices powered by ISRO's GSAT satellites have been installed on over 10,000 locomotives, providing automatic train tracking and arrival/departure updates at stations.",
                "url": "https://isro.gov.in/press-release/isro-railways-rtis-satellite-tracking",
                "tags": ["General Science", "Transportation", "Infrastructure & Technology"]
            }
        ]

    def collect(self, exam_type: str) -> List[Dict[str, Any]]:
        """Simulates news retrieval for the specified exam category.
        
        Returns all mock articles.
        """
        print(f"[NewsCollector] Collecting articles for exam type: {exam_type}")
        return self.mock_db
