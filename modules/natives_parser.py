import re
import glob
from modules.get_requests import print_with_time


def parse_exchange_summary():
    file_pattern = './logs/history/paths*.html'
    file_paths = glob.glob(file_pattern)
    if not file_paths:
        print_with_time("  Файлы HTML не найдены в указанной директории.")
        return

    latest_file_path = max(file_paths, key=lambda f: int(re.search(r'\d+', f).group()))
    with open(latest_file_path, 'r') as file:
        html_content = file.read()

    exchange_summary_pattern = r'<pre class="exchange_summary">(.+?)<\/pre>'
    match = re.search(exchange_summary_pattern, html_content)

    if match:
        exchange_summary = match.group(1).strip()
        values = re.findall(r'\d+\.\d+|\w+', exchange_summary)

        exchange_dict = {}
        for i in range(0, len(values), 2):
            currency = values[i+1]
            amount = float(values[i])
            exchange_dict[currency] = amount

        return exchange_dict
    else:
        print_with_time("  Тег <pre> с классом 'exchange_summary' не найден в файле HTML.")
        return {}
