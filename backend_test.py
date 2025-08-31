#!/usr/bin/env python3
"""
Backend API Tests for School Student Absence Tracking System
Tests French data structure, date validation, CRUD operations, statistics, and Excel export
"""

import requests
import json
import sys
from datetime import datetime
import os

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return "https://class-attendance-5.preview.emergentagent.com"

BASE_URL = get_backend_url() + "/api"
print(f"Testing backend at: {BASE_URL}")

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def assert_test(self, condition, test_name, error_msg=""):
        if condition:
            print(f"✅ PASS: {test_name}")
            self.passed += 1
        else:
            print(f"❌ FAIL: {test_name} - {error_msg}")
            self.failed += 1
            self.errors.append(f"{test_name}: {error_msg}")
    
    def print_summary(self):
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed} passed, {self.failed} failed")
        if self.errors:
            print(f"\nERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}")

def test_api_root():
    """Test API root endpoint"""
    results = TestResults()
    try:
        response = requests.get(f"{BASE_URL}/")
        results.assert_test(
            response.status_code == 200,
            "API Root Endpoint",
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            data = response.json()
            results.assert_test(
                "message" in data and "API du Suivi des Absences Scolaires" in data["message"],
                "API Root Message in French",
                f"Response: {data}"
            )
    except Exception as e:
        results.assert_test(False, "API Root Endpoint", f"Exception: {str(e)}")
    
    return results

def test_classes_endpoint():
    """Test the 18 French classes endpoint"""
    results = TestResults()
    
    expected_classes = [
        "Salle 2", "Salle 5", "Salle 6", "Salle 7", "Salle 8", "Salle 9", 
        "Salle 10", "Salle 11", "Salle 12", "Salle 13", "Salle 14", "Salle 16", "Salle 18",
        "Nuage", "Soleil", "Arc-en-ciel", "Lune", "Étoile"
    ]
    
    try:
        response = requests.get(f"{BASE_URL}/classes")
        results.assert_test(
            response.status_code == 200,
            "Classes Endpoint Status",
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            data = response.json()
            classes = data.get("classes", [])
            
            results.assert_test(
                len(classes) == 18,
                "18 Classes Count",
                f"Found {len(classes)} classes"
            )
            
            # Test specific French classes mentioned in requirements
            test_classes = ["Salle 2", "Nuage", "Arc-en-ciel"]
            for test_class in test_classes:
                results.assert_test(
                    test_class in classes,
                    f"Class '{test_class}' Present",
                    f"Class not found in: {classes}"
                )
                
            # Test all expected classes
            for expected_class in expected_classes:
                results.assert_test(
                    expected_class in classes,
                    f"Expected Class '{expected_class}'",
                    f"Missing from: {classes}"
                )
                
    except Exception as e:
        results.assert_test(False, "Classes Endpoint", f"Exception: {str(e)}")
    
    return results

def test_absence_crud_operations():
    """Test CRUD operations for absences with French data structure"""
    results = TestResults()
    created_absence_ids = []
    
    # Test data with French structure
    test_absences = [
        {
            "classe": "Salle 2",
            "date": "31/08/2025",
            "nom": "Dupont",
            "prenom": "Jean",
            "motif": "M",
            "justifie": "N",
            "remarques": "Absence non justifiée"
        },
        {
            "classe": "Nuage",
            "date": "01/09/2025",
            "nom": "Martin",
            "prenom": "Marie",
            "motif": "RDV",
            "justifie": "O",
            "remarques": "Rendez-vous médical"
        },
        {
            "classe": "Arc-en-ciel",
            "date": "02/09/2025",
            "nom": "Bernard",
            "prenom": "Pierre",
            "motif": "F",
            "justifie": "N",
            "remarques": ""
        }
    ]
    
    # Test CREATE operations
    for i, absence_data in enumerate(test_absences):
        try:
            response = requests.post(f"{BASE_URL}/absences", json=absence_data)
            results.assert_test(
                response.status_code == 200,
                f"Create Absence {i+1} Status",
                f"Status: {response.status_code}, Response: {response.text}"
            )
            
            if response.status_code == 200:
                created_absence = response.json()
                absence_id = created_absence.get("id")
                if absence_id:
                    created_absence_ids.append(absence_id)
                
                # Verify French data structure
                results.assert_test(
                    created_absence.get("nom") == absence_data["nom"],
                    f"Absence {i+1} - Nom Field",
                    f"Expected: {absence_data['nom']}, Got: {created_absence.get('nom')}"
                )
                
                results.assert_test(
                    created_absence.get("prenom") == absence_data["prenom"],
                    f"Absence {i+1} - Prenom Field",
                    f"Expected: {absence_data['prenom']}, Got: {created_absence.get('prenom')}"
                )
                
                results.assert_test(
                    created_absence.get("motif") == absence_data["motif"],
                    f"Absence {i+1} - Motif Field",
                    f"Expected: {absence_data['motif']}, Got: {created_absence.get('motif')}"
                )
                
                results.assert_test(
                    created_absence.get("justifie") == absence_data["justifie"],
                    f"Absence {i+1} - Justifie Field",
                    f"Expected: {absence_data['justifie']}, Got: {created_absence.get('justifie')}"
                )
                
        except Exception as e:
            results.assert_test(False, f"Create Absence {i+1}", f"Exception: {str(e)}")
    
    # Test READ operations - Get all absences
    try:
        response = requests.get(f"{BASE_URL}/absences")
        results.assert_test(
            response.status_code == 200,
            "Get All Absences Status",
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            absences = response.json()
            results.assert_test(
                len(absences) >= len(created_absence_ids),
                "Get All Absences Count",
                f"Expected at least {len(created_absence_ids)}, got {len(absences)}"
            )
    except Exception as e:
        results.assert_test(False, "Get All Absences", f"Exception: {str(e)}")
    
    # Test READ operations - Filter by class
    for test_class in ["Salle 2", "Nuage", "Arc-en-ciel"]:
        try:
            response = requests.get(f"{BASE_URL}/absences", params={"classe": test_class})
            results.assert_test(
                response.status_code == 200,
                f"Get Absences for {test_class} Status",
                f"Status: {response.status_code}"
            )
            
            if response.status_code == 200:
                class_absences = response.json()
                # Verify all returned absences are for the correct class
                for absence in class_absences:
                    results.assert_test(
                        absence.get("classe") == test_class,
                        f"Class Filter Accuracy for {test_class}",
                        f"Found absence for class {absence.get('classe')} when filtering for {test_class}"
                    )
        except Exception as e:
            results.assert_test(False, f"Get Absences for {test_class}", f"Exception: {str(e)}")
    
    # Test DELETE operations
    for i, absence_id in enumerate(created_absence_ids):
        try:
            response = requests.delete(f"{BASE_URL}/absences/{absence_id}")
            results.assert_test(
                response.status_code == 200,
                f"Delete Absence {i+1} Status",
                f"Status: {response.status_code}, Response: {response.text}"
            )
        except Exception as e:
            results.assert_test(False, f"Delete Absence {i+1}", f"Exception: {str(e)}")
    
    return results

def test_french_date_validation():
    """Test French date format validation (DD/MM/YYYY)"""
    results = TestResults()
    
    # Valid French dates
    valid_dates = ["31/08/2025", "01/09/2025", "29/02/2024", "15/12/2025"]
    
    # Invalid dates
    invalid_dates = [
        "31/13/2025",  # Invalid month
        "2025/08/31",  # Wrong format (YYYY/MM/DD)
        "08/31/2025",  # US format (MM/DD/YYYY)
        "32/01/2025",  # Invalid day
        "29/02/2025",  # Invalid leap year
        "31/04/2025",  # April doesn't have 31 days
        "invalid-date",
        "2025-08-31"   # ISO format
    ]
    
    base_absence = {
        "classe": "Salle 2",
        "nom": "Dupont",
        "prenom": "Jean",
        "motif": "M",
        "justifie": "N",
        "remarques": "Test date validation"
    }
    
    # Test valid dates
    for valid_date in valid_dates:
        try:
            absence_data = {**base_absence, "date": valid_date}
            response = requests.post(f"{BASE_URL}/absences", json=absence_data)
            results.assert_test(
                response.status_code == 200,
                f"Valid Date '{valid_date}' Accepted",
                f"Status: {response.status_code}, Response: {response.text}"
            )
            
            # Clean up - delete the created absence
            if response.status_code == 200:
                created_absence = response.json()
                absence_id = created_absence.get("id")
                if absence_id:
                    requests.delete(f"{BASE_URL}/absences/{absence_id}")
                    
        except Exception as e:
            results.assert_test(False, f"Valid Date '{valid_date}'", f"Exception: {str(e)}")
    
    # Test invalid dates
    for invalid_date in invalid_dates:
        try:
            absence_data = {**base_absence, "date": invalid_date}
            response = requests.post(f"{BASE_URL}/absences", json=absence_data)
            results.assert_test(
                response.status_code == 400,
                f"Invalid Date '{invalid_date}' Rejected",
                f"Status: {response.status_code} (should be 400), Response: {response.text}"
            )
        except Exception as e:
            results.assert_test(False, f"Invalid Date '{invalid_date}'", f"Exception: {str(e)}")
    
    return results

def test_statistics_calculation():
    """Test statistics calculation for total, unjustified, and recent absences"""
    results = TestResults()
    
    # Create test data for statistics
    test_data = [
        {"classe": "Salle 2", "date": "01/09/2025", "nom": "Dupont", "prenom": "Jean", "motif": "M", "justifie": "N"},
        {"classe": "Salle 2", "date": "02/09/2025", "nom": "Martin", "prenom": "Marie", "motif": "RDV", "justifie": "O"},
        {"classe": "Nuage", "date": "01/09/2025", "nom": "Bernard", "prenom": "Pierre", "motif": "F", "justifie": "N"},
        {"classe": "Nuage", "date": "03/09/2025", "nom": "Leroy", "prenom": "Sophie", "motif": "A", "justifie": "N"},
    ]
    
    created_ids = []
    
    # Create test absences
    for absence_data in test_data:
        try:
            response = requests.post(f"{BASE_URL}/absences", json=absence_data)
            if response.status_code == 200:
                created_absence = response.json()
                created_ids.append(created_absence.get("id"))
        except:
            pass
    
    # Test statistics endpoint
    try:
        response = requests.get(f"{BASE_URL}/stats")
        results.assert_test(
            response.status_code == 200,
            "Statistics Endpoint Status",
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            stats = response.json()
            
            # Should have stats for all 18 classes
            results.assert_test(
                len(stats) == 18,
                "Statistics for All 18 Classes",
                f"Got stats for {len(stats)} classes"
            )
            
            # Find stats for our test classes
            salle2_stats = next((s for s in stats if s["classe"] == "Salle 2"), None)
            nuage_stats = next((s for s in stats if s["classe"] == "Nuage"), None)
            
            if salle2_stats:
                results.assert_test(
                    salle2_stats["total_absences"] >= 2,
                    "Salle 2 Total Absences Count",
                    f"Expected >= 2, got {salle2_stats['total_absences']}"
                )
                
                results.assert_test(
                    salle2_stats["absences_non_justifiees"] >= 1,
                    "Salle 2 Unjustified Absences Count",
                    f"Expected >= 1, got {salle2_stats['absences_non_justifiees']}"
                )
                
                results.assert_test(
                    "absences_recentes" in salle2_stats,
                    "Salle 2 Recent Absences Field Present",
                    f"Stats: {salle2_stats}"
                )
            
            if nuage_stats:
                results.assert_test(
                    nuage_stats["total_absences"] >= 2,
                    "Nuage Total Absences Count",
                    f"Expected >= 2, got {nuage_stats['total_absences']}"
                )
                
                results.assert_test(
                    nuage_stats["absences_non_justifiees"] >= 2,
                    "Nuage Unjustified Absences Count",
                    f"Expected >= 2, got {nuage_stats['absences_non_justifiees']}"
                )
            
            # Test that all required fields are present
            for stat in stats:
                required_fields = ["classe", "total_absences", "absences_non_justifiees", "absences_recentes"]
                for field in required_fields:
                    results.assert_test(
                        field in stat,
                        f"Statistics Field '{field}' for {stat.get('classe', 'Unknown')}",
                        f"Missing field in: {stat}"
                    )
                    
    except Exception as e:
        results.assert_test(False, "Statistics Endpoint", f"Exception: {str(e)}")
    
    # Clean up test data
    for absence_id in created_ids:
        try:
            requests.delete(f"{BASE_URL}/absences/{absence_id}")
        except:
            pass
    
    return results

def test_excel_export():
    """Test Excel export functionality for individual and all classes"""
    results = TestResults()
    
    # Create some test data for export
    test_data = [
        {"classe": "Salle 2", "date": "01/09/2025", "nom": "Dupont", "prenom": "Jean", "motif": "M", "justifie": "N", "remarques": "Test export"},
        {"classe": "Nuage", "date": "02/09/2025", "nom": "Martin", "prenom": "Marie", "motif": "RDV", "justifie": "O", "remarques": "Export test"},
    ]
    
    created_ids = []
    
    # Create test absences
    for absence_data in test_data:
        try:
            response = requests.post(f"{BASE_URL}/absences", json=absence_data)
            if response.status_code == 200:
                created_absence = response.json()
                created_ids.append(created_absence.get("id"))
        except:
            pass
    
    # Test individual class export
    test_classes = ["Salle 2", "Nuage"]
    for test_class in test_classes:
        try:
            response = requests.get(f"{BASE_URL}/export/excel", params={"classe": test_class})
            results.assert_test(
                response.status_code == 200,
                f"Excel Export for {test_class} Status",
                f"Status: {response.status_code}"
            )
            
            if response.status_code == 200:
                # Check content type
                content_type = response.headers.get('content-type', '')
                results.assert_test(
                    'spreadsheet' in content_type or 'excel' in content_type,
                    f"Excel Export for {test_class} Content Type",
                    f"Content-Type: {content_type}"
                )
                
                # Check content disposition (filename)
                content_disposition = response.headers.get('content-disposition', '')
                results.assert_test(
                    f"absences_{test_class}.xlsx" in content_disposition,
                    f"Excel Export for {test_class} Filename",
                    f"Content-Disposition: {content_disposition}"
                )
                
                # Check that we got actual content
                results.assert_test(
                    len(response.content) > 0,
                    f"Excel Export for {test_class} Has Content",
                    f"Content length: {len(response.content)}"
                )
                
        except Exception as e:
            results.assert_test(False, f"Excel Export for {test_class}", f"Exception: {str(e)}")
    
    # Test all classes export
    try:
        response = requests.get(f"{BASE_URL}/export/excel")
        results.assert_test(
            response.status_code == 200,
            "Excel Export All Classes Status",
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            # Check content type
            content_type = response.headers.get('content-type', '')
            results.assert_test(
                'spreadsheet' in content_type or 'excel' in content_type,
                "Excel Export All Classes Content Type",
                f"Content-Type: {content_type}"
            )
            
            # Check filename
            content_disposition = response.headers.get('content-disposition', '')
            results.assert_test(
                "absences_toutes_classes.xlsx" in content_disposition,
                "Excel Export All Classes Filename",
                f"Content-Disposition: {content_disposition}"
            )
            
            # Check that we got actual content
            results.assert_test(
                len(response.content) > 0,
                "Excel Export All Classes Has Content",
                f"Content length: {len(response.content)}"
            )
            
    except Exception as e:
        results.assert_test(False, "Excel Export All Classes", f"Exception: {str(e)}")
    
    # Clean up test data
    for absence_id in created_ids:
        try:
            requests.delete(f"{BASE_URL}/absences/{absence_id}")
        except:
            pass
    
    return results

def test_validation_edge_cases():
    """Test edge cases and validation"""
    results = TestResults()
    
    # Test invalid class
    invalid_class_data = {
        "classe": "Invalid Class",
        "date": "01/09/2025",
        "nom": "Dupont",
        "prenom": "Jean",
        "motif": "M",
        "justifie": "N"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/absences", json=invalid_class_data)
        results.assert_test(
            response.status_code == 400,
            "Invalid Class Rejected",
            f"Status: {response.status_code} (should be 400)"
        )
    except Exception as e:
        results.assert_test(False, "Invalid Class Test", f"Exception: {str(e)}")
    
    # Test invalid motif
    invalid_motif_data = {
        "classe": "Salle 2",
        "date": "01/09/2025",
        "nom": "Dupont",
        "prenom": "Jean",
        "motif": "INVALID",
        "justifie": "N"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/absences", json=invalid_motif_data)
        results.assert_test(
            response.status_code == 400,
            "Invalid Motif Rejected",
            f"Status: {response.status_code} (should be 400)"
        )
    except Exception as e:
        results.assert_test(False, "Invalid Motif Test", f"Exception: {str(e)}")
    
    # Test invalid justifie
    invalid_justifie_data = {
        "classe": "Salle 2",
        "date": "01/09/2025",
        "nom": "Dupont",
        "prenom": "Jean",
        "motif": "M",
        "justifie": "INVALID"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/absences", json=invalid_justifie_data)
        results.assert_test(
            response.status_code == 400,
            "Invalid Justifie Rejected",
            f"Status: {response.status_code} (should be 400)"
        )
    except Exception as e:
        results.assert_test(False, "Invalid Justifie Test", f"Exception: {str(e)}")
    
    # Test delete non-existent absence
    try:
        response = requests.delete(f"{BASE_URL}/absences/non-existent-id")
        results.assert_test(
            response.status_code == 404,
            "Delete Non-existent Absence",
            f"Status: {response.status_code} (should be 404)"
        )
    except Exception as e:
        results.assert_test(False, "Delete Non-existent Test", f"Exception: {str(e)}")
    
    return results

def main():
    """Run all backend tests"""
    print("🏫 School Student Absence Tracking API - Backend Tests")
    print("=" * 60)
    
    all_results = TestResults()
    
    # Run all test suites
    test_suites = [
        ("API Root", test_api_root),
        ("18 French Classes", test_classes_endpoint),
        ("Absence CRUD Operations", test_absence_crud_operations),
        ("French Date Validation", test_french_date_validation),
        ("Statistics Calculation", test_statistics_calculation),
        ("Excel Export", test_excel_export),
        ("Validation Edge Cases", test_validation_edge_cases)
    ]
    
    for suite_name, test_function in test_suites:
        print(f"\n📋 Testing: {suite_name}")
        print("-" * 40)
        
        suite_results = test_function()
        
        # Aggregate results
        all_results.passed += suite_results.passed
        all_results.failed += suite_results.failed
        all_results.errors.extend(suite_results.errors)
        
        print(f"Suite Results: {suite_results.passed} passed, {suite_results.failed} failed")
    
    # Print final summary
    all_results.print_summary()
    
    # Return exit code
    return 0 if all_results.failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())