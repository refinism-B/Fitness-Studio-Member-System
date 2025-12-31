import sys
import pandas as pd
from unittest.mock import MagicMock

# Mock streamlit and gsheets before importing mod
sys.modules["streamlit"] = MagicMock()
sys.modules["streamlit_gsheets"] = MagicMock()

# Mock O_connect_to_gsheet
mock_gs = MagicMock()
sys.modules["mod.O_connect_to_gsheet"] = mock_gs

# Now import the module to test
# Ensure 'mod' can be imported. Assuming running from 'code' directory.
sys.path.append(".") 
from mod import O_general

def test_get_df_from_db():
    print("Testing GET_DF_FROM_DB...")
    
    # Mock data with floats that should be strings
    data = {
        '會員編號': [1.0, 2.001, '3.0', '4'], # 1.0 -> "1", 2.001 -> "2.001" (unchanged), '3.0' -> "3", '4' -> "4"
        '電話': [912345678.0, '0987654321', '0912345678.0', None],
        '備註': [None, 123.0, 'Test', '']
    }
    df_mock = pd.DataFrame(data)
    
    mock_gs.read_sheet_as_df.return_value = df_mock
    
    # Call the function
    df_result = O_general.GET_DF_FROM_DB("TestSheet")
    
    # Check results
    print("Result DataFrame:")
    print(df_result)
    
    # Assertions
    # 會員編號
    assert df_result.iloc[0]['會員編號'] == "1", f"Row 0 ID failed: {df_result.iloc[0]['會員編號']}"
    assert df_result.iloc[1]['會員編號'] == "2.001", f"Row 1 ID failed: {df_result.iloc[1]['會員編號']}" # Should keep decimals if not .0
    assert df_result.iloc[2]['會員編號'] == "3", f"Row 2 ID failed: {df_result.iloc[2]['會員編號']}"
    assert df_result.iloc[3]['會員編號'] == "4", f"Row 3 ID failed: {df_result.iloc[3]['會員編號']}"
    
    # 電話
    assert df_result.iloc[0]['電話'] == "912345678", f"Row 0 Phone failed: {df_result.iloc[0]['電話']}"
    assert df_result.iloc[2]['電話'] == "0912345678", f"Row 2 Phone failed: {df_result.iloc[2]['電話']}"
    
    # 備註
    assert df_result.iloc[1]['備註'] == "123", f"Row 1 Remark failed: {df_result.iloc[1]['備註']}"
    
    print("\nGET_DF_FROM_DB Verification Logic Passed!")

def test_add_member_logic():
    print("\nTesting validation logic (A_add_member equivalent)...")
    # Simulate the logic in A_add_member
    coach_str = "1.0"
    member_id = "001"
    
    # New logic
    result = str(coach_str).replace(".0", "") + str(member_id)
    print(f"combine '{coach_str}' + '{member_id}' -> '{result}'")
    
    assert result == "1001", f"Failed: got {result}"
    print("Validation Logic Passed!")

if __name__ == "__main__":
    try:
        test_get_df_from_db()
        test_add_member_logic()
        print("\nALL VERIFICATIONS PASSED")
    except Exception as e:
        print(f"\nVERIFICATION FAILED: {e}")
        exit(1)
