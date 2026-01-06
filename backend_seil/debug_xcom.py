import sys
try:
    from airflow.models.xcom import XCom
    print(f"XCom Class: {XCom}")
    print(f"Dir XCom: {dir(XCom)}")
    
    # Check inheritance
    print(f"MRO: {XCom.mro()}")
    
except Exception as e:
    print(f"Error importing XCom: {e}")
