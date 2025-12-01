import sqlite3
from tabulate import tabulate
import os

class CustomerManagementSystem:
    def __init__(self, db_name='customers.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.initialize_database()

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def initialize_database(self):
        self.connect()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            company TEXT,
            position TEXT,
            memo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()
        self.close()

    def add_customer(self, name, phone='', email='', company='', position='', memo=''):
        self.connect()
        self.cursor.execute('''
        INSERT INTO customers (name, phone, email, company, position, memo)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, phone, email, company, position, memo))
        self.conn.commit()
        self.close()
        print(f"\n고객 '{name}'이(가) 성공적으로 추가되었습니다.")

    def list_customers(self):
        self.connect()
        self.cursor.execute('SELECT * FROM customers ORDER BY name')
        customers = self.cursor.fetchall()
        self.close()
        
        if not customers:
            print("\n등록된 고객이 없습니다.")
            return
            
        headers = ["ID", "이름", "전화번호", "이메일", "회사", "직책", "메모", "등록일"]
        print("\n=== 고객 목록 ===")
        print(tabulate(customers, headers=headers, tablefmt="grid"))

    def search_customers(self, keyword):
        self.connect()
        self.cursor.execute('''
        SELECT * FROM customers 
        WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? OR company LIKE ?
        ORDER BY name
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        customers = self.cursor.fetchall()
        self.close()
        
        if not customers:
            print(f"\n'{keyword}'에 해당하는 고객을 찾을 수 없습니다.")
            return
            
        headers = ["ID", "이름", "전화번호", "이메일", "회사", "직책", "메모", "등록일"]
        print(f"\n=== '{keyword}' 검색 결과 ===")
        print(tabulate(customers, headers=headers, tablefmt="grid"))

    def update_customer(self, customer_id, **kwargs):
        if not kwargs:
            print("\n수정할 정보를 입력해주세요.")
            return
            
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(customer_id)
        
        self.connect()
        self.cursor.execute(f'''
        UPDATE customers 
        SET {set_clause}
        WHERE id = ?
        ''', values)
        
        if self.cursor.rowcount > 0:
            self.conn.commit()
            print(f"\n고객 ID {customer_id}의 정보가 성공적으로 수정되었습니다.")
        else:
            print(f"\n고객 ID {customer_id}를 찾을 수 없습니다.")
            
        self.close()

    def delete_customer(self, customer_id):
        self.connect()
        self.cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
        
        if self.cursor.rowcount > 0:
            self.conn.commit()
            print(f"\n고객 ID {customer_id}가 성공적으로 삭제되었습니다.")
        else:
            print(f"\n고객 ID {customer_id}를 찾을 수 없습니다.")
            
        self.close()

def display_menu():
    print("\n=== 고객 관리 시스템 ===")
    print("1. 고객 목록 보기")
    print("2. 고객 검색")
    print("3. 고객 추가")
    print("4. 고객 정보 수정")
    print("5. 고객 삭제")
    print("0. 종료")
    return input("\n원하는 작업을 선택하세요: ")

def main():
    crm = CustomerManagementSystem()
    
    while True:
        try:
            choice = display_menu()
            
            if choice == '1':
                crm.list_customers()
                
            elif choice == '2':
                keyword = input("\n검색할 고객 정보를 입력하세요: ").strip()
                if keyword:
                    crm.search_customers(keyword)
                else:
                    print("\n검색어를 입력해주세요.")
                    
            elif choice == '3':
                print("\n=== 새 고객 추가 ===")
                name = input("이름: ").strip()
                if not name:
                    print("\n이름은 필수 입력 항목입니다.")
                    continue
                    
                phone = input("전화번호 (선택사항): ").strip()
                email = input("이메일 (선택사항): ").strip()
                company = input("회사명 (선택사항): ").strip()
                position = input("직책 (선택사항): ").strip()
                memo = input("메모 (선택사항): ").strip()
                
                crm.add_customer(name, phone, email, company, position, memo)
                
            elif choice == '4':
                crm.list_customers()
                try:
                    customer_id = int(input("\n수정할 고객의 ID를 입력하세요: ").strip())
                except ValueError:
                    print("\n올바른 ID를 입력해주세요.")
                    continue
                    
                print("\n수정할 정보를 입력하세요 (수정하지 않을 항목은 엔터를 눌러 건너뜁니다):")
                updates = {}
                
                name = input("이름: ").strip()
                if name: updates['name'] = name
                phone = input("전화번호: ").strip()
                if phone: updates['phone'] = phone
                email = input("이메일: ").strip()
                if email: updates['email'] = email
                company = input("회사명: ").strip()
                if company: updates['company'] = company
                position = input("직책: ").strip()
                if position: updates['position'] = position
                memo = input("메모: ").strip()
                if memo: updates['memo'] = memo
                
                if updates:
                    crm.update_customer(customer_id, **updates)
                else:
                    print("\n수정할 정보가 없습니다.")
                    
            elif choice == '5':
                crm.list_customers()
                try:
                    customer_id = int(input("\n삭제할 고객의 ID를 입력하세요: ").strip())
                    confirm = input(f"\n정말로 고객 ID {customer_id}를 삭제하시겠습니까? (y/n): ").strip().lower()
                    if confirm == 'y':
                        crm.delete_customer(customer_id)
                except ValueError:
                    print("\n올바른 ID를 입력해주세요.")
                    
            elif choice == '0':
                print("\n고객 관리 시스템을 종료합니다.")
                break
                
            else:
                print("\n잘못된 선택입니다. 다시 시도해주세요.")
                
        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"\n오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
