import sys
import csv
import struct

class UVMAssembler:
    def __init__(self):
        self.commands = []
        
    # Парсинг CSV и преобразование в промежуточное представление
    def parse_csv(self, input_file):
        commands = []
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or row[0].startswith('#'):  # Пропускаем пустые строки и комментарии
                    continue
                    
                cmd_type = row[0].strip().upper()
                
                if cmd_type == 'LOAD_CONST':
                    # LOAD_CONST, константа
                    if len(row) < 2:
                        raise ValueError(f"Неверный формат команды LOAD_CONST: {row}")
                    constant = int(row[1])
                    commands.append({'type': 'LOAD_CONST', 'A': 5, 'B': constant})
                    
                elif cmd_type == 'READ_MEM':
                    # READ_MEM
                    commands.append({'type': 'READ_MEM', 'A': 4})
                    
                elif cmd_type == 'WRITE_MEM':
                    # WRITE_MEM
                    commands.append({'type': 'WRITE_MEM', 'A': 7})
                    
                elif cmd_type == 'ABS':
                    # ABS, адрес
                    if len(row) < 2:
                        raise ValueError(f"Неверный формат команды ABS: {row}")
                    address = int(row[1])
                    commands.append({'type': 'ABS', 'A': 2, 'B': address})
                    
                else:
                    raise ValueError(f"Неизвестная команда: {cmd_type}")
                    
        return commands
    
    # Вывод промежуточного представления в формате полей
    def display_intermediate(self, commands):
        print("Промежуточное представление программы:")
        print("-" * 50)
        for i, cmd in enumerate(commands):
            print(f"Команда {i}: {cmd['type']}")
            print(f"  Поле A: {cmd['A']} (биты 0-2)")
            if 'B' in cmd:
                print(f"  Поле B: {cmd['B']} (биты 3-{28 if cmd['type'] == 'LOAD_CONST' else 14})")
            print()
    
    # Проверка тестовых случаев из спецификации
    def test_specification(self):
        test_cases = [
            # LOAD_CONST: A=5, B=129
            {'type': 'LOAD_CONST', 'A': 5, 'B': 129},
            # READ_MEM: A=4
            {'type': 'READ_MEM', 'A': 4},
            # WRITE_MEM: A=7
            {'type': 'WRITE_MEM', 'A': 7},
            # ABS: A=2, B=137
            {'type': 'ABS', 'A': 2, 'B': 137}
        ]
        
        print("Тестовые случаи из спецификации УВМ:")
        print("-" * 40)
        for i, test in enumerate(test_cases):
            print(f"Тест {i+1}: {test}")
        print()
        
        return test_cases

def main():
    if len(sys.argv) < 4:
        print("Использование: python assembler.py <input.csv> <output.bin> --test")
        print("  --test - режим тестирования (вывод промежуточного представления)")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    test_mode = len(sys.argv) > 3 and sys.argv[3] == '--test'
    
    assembler = UVMAssembler()
    
    try:
        # Парсинг CSV файла
        commands = assembler.parse_csv(input_file)
        
        if test_mode:
            # Вывод промежуточного представления
            assembler.display_intermediate(commands)
            
            # Проверка тестовых случаев
            spec_tests = assembler.test_specification()
            
            print("Сравнение с тестами спецификации:")
            print("-" * 35)
            for i, (parsed, spec) in enumerate(zip(commands[:4], spec_tests)):
                match = parsed == spec
                status = "✓ СОВПАДАЕТ" if match else "✗ НЕ СОВПАДАЕТ"
                print(f"Команда {i}: {status}")
                if not match:
                    print(f"  Получено: {parsed}")
                    print(f"  Ожидалось: {spec}")
            print()
        
        print(f"Успешно ассемблировано {len(commands)} команд")
        
    except Exception as e:
        print(f"Ошибка ассемблирования: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
