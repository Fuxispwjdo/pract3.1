import sys
import csv
import json

class UVMAssemblerStage1:
    def __init__(self):
        self.commands = []
    
    def parse_csv(self, input_file):
        """Парсинг CSV файла в формате: код_операции,аргумент"""
        commands = []
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                line_num = 0
                
                for row in reader:
                    line_num += 1
                    
                    # Пропускаем пустые строки и комментарии
                    if not row or not row[0] or row[0].strip().startswith('#'):
                        continue
                    
                    # Убираем лишние пробелы
                    row = [cell.strip() for cell in row]
                    
                    # Получаем код операции
                    try:
                        opcode = int(row[0])
                    except ValueError:
                        print(f"Ошибка в строке {line_num}: некорректный код операции '{row[0]}'")
                        continue
                    
                    # Получаем аргумент (если есть)
                    arg = None
                    if len(row) > 1 and row[1] != '':
                        try:
                            arg = int(row[1])
                        except ValueError:
                            print(f"Ошибка в строке {line_num}: некорректный аргумент '{row[1]}'")
                            continue
                    
                    commands.append({
                        'opcode': opcode,
                        'arg': arg,
                        'line': line_num
                    })
            
            return commands
            
        except FileNotFoundError:
            print(f"Файл '{input_file}' не найден!")
            return []
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
            return []
    
    def encode_to_hex(self, commands):
        """Кодирование команд в hex представление"""
        hex_results = []
        
        for cmd in commands:
            opcode = cmd['opcode']
            arg = cmd['arg']
            
            if opcode == 5:  # LOAD_CONST
                # A=5 (биты 0-2), B=константа (биты 3-28)
                encoded = (arg << 3) | opcode
            elif opcode == 4:  # READ_MEM
                # A=4 (биты 0-2)
                encoded = opcode
            elif opcode == 7:  # WRITE_MEM
                # A=7 (биты 0-2)
                encoded = opcode
            elif opcode == 2:  # ABS
                # A=2 (биты 0-2), B=адрес (биты 3-14)
                encoded = ((arg & 0xFFF) << 3) | opcode
            else:
                encoded = opcode
            
            # Конвертируем в hex байты (little-endian, 4 байта)
            hex_bytes = []
            for i in range(4):
                byte = (encoded >> (i * 8)) & 0xFF
                hex_bytes.append(f"0x{byte:02X}")
            
            hex_results.append({
                'cmd': cmd,
                'encoded': encoded,
                'hex_bytes': hex_bytes,
                'hex_string': ', '.join(hex_bytes)
            })
        
        return hex_results
    
    def display_test_format(self, commands, hex_results):
        """Вывод в формате тестирования с hex представлением"""
        for i, (cmd, hex_data) in enumerate(zip(commands, hex_results)):
            opcode = cmd['opcode']
            arg = cmd['arg']
            
            if arg is not None:
                print(f"A={opcode}, B={arg}")
            else:
                print(f"A={opcode}")
            
            # Выводим hex представление
            print(f"HEX: {hex_data['hex_string']}")
    
    def display_detailed(self, commands, hex_results):
        """Подробный вывод промежуточного представления"""
        for i, (cmd, hex_data) in enumerate(zip(commands, hex_results)):
            opcode = cmd['opcode']
            arg = cmd['arg']
            
            # Определяем тип команды
            cmd_type = "UNKNOWN"
            if opcode == 5:
                cmd_type = "LOAD_CONST"
            elif opcode == 4:
                cmd_type = "READ_MEM"
            elif opcode == 7:
                cmd_type = "WRITE_MEM"
            elif opcode == 2:
                cmd_type = "ABS"
            
            print(f"\nКоманда {i+1} (строка {cmd['line']}):")
            print(f"  Тип: {cmd_type}")
            print(f"  Код операции: {opcode}")
            print(f"  Аргумент: {arg if arg is not None else 'нет'}")
            
            # Битовое представление
            if cmd_type == "LOAD_CONST":
                print(f"  Биты: A={opcode} (0-2), B={arg} (3-28)")
            elif cmd_type == "ABS":
                print(f"  Биты: A={opcode} (0-2), B={arg} (3-14)")
            else:
                print(f"  Биты: A={opcode} (0-2)")
            
            # Hex представление
            print(f"  HEX: {hex_data['hex_string']}")
            print(f"  Декодированное значение: {hex_data['encoded']}")

def create_test_file():
    
    filename = "test_program.csv"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(test_content)
    except Exception as e:
        print(f"Ошибка создания файла: {e}")

def main():
    # Создаем тестовый файл, если его нет
    import os
    if not os.path.exists("test_program.csv"):
        print("Создан тестовый файл")
        create_test_file()
    
    # Используем аргументы командной строки
    if len(sys.argv) < 4:
        print("Использование: python assembler.py <input.csv> <output.bin> --test")
        print("Пример: python assembler.py test_program.csv program.bin --test")
        print("\nБудет использован тестовый режим с выводом hex представления")
        
        # По умолчанию используем тестовый файл
        input_file = "test_program.csv"
        test_mode = True
    else:
        input_file = sys.argv[1]
        # output_file = sys.argv[2]  # Не используется на этапе 1
        test_mode = sys.argv[3] == "--test"
    
    assembler = UVMAssemblerStage1()
    
    # Парсим файл
    commands = assembler.parse_csv(input_file)
    
    if not commands:
        print(f"\nНе удалось загрузить команды из файла: {input_file}")
        return
    
    # Кодируем в hex
    hex_results = assembler.encode_to_hex(commands)

    if test_mode:
        # Вывод в формате тестирования с hex
        for i, (cmd, hex_data) in enumerate(zip(commands, hex_results)):
            opcode = cmd['opcode']
            arg = cmd['arg']
            
            if arg is not None:
                print(f"A={opcode}, B={arg}")
            else:
                print(f"A={opcode}")
            
            # Выводим hex представление как в спецификации
            print(f"HEX: {hex_data['hex_string']}")
    else:
        # Подробный вывод
        assembler.display_detailed(commands, hex_results)
    
    print(f"\nОбработано {len(commands)} команд")
    
    # Сохраняем промежуточное представление для следующего этапа
    intermediate_data = []
    for cmd, hex_data in zip(commands, hex_results):
        intermediate_data.append({
            'opcode': cmd['opcode'],
            'arg': cmd['arg'],
            'hex': hex_data['hex_bytes'],
            'encoded': hex_data['encoded']
        })
    
    json_file = "intermediate.json"
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(intermediate_data, f, indent=2, ensure_ascii=False)
        print(f"Промежуточное представление сохранено в: {json_file}")
    except Exception as e:
        print(f"Ошибка сохранения JSON: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"\nНеожиданная ошибка: {e}")