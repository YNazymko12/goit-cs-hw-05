import requests
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import re
from colorama import Fore, Style, init

# Ініціалізація colorama
init(autoreset=True)


def fetch_text_from_url(url):
    """Завантажує текст із заданої URL-адреси."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def map_function(text):
    """Розбиває текст на слова і повертає список пар (слово, 1)."""
    words = re.findall(r'\b\w+\b', text.lower())
    return [(word, 1) for word in words]


def shuffle_function(mapped_values):
    """Групує слова за ключем."""
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(shuffled_values):
    """Рахує кількість кожного слова."""
    reduced = {}
    for key, values in shuffled_values:
        reduced[key] = sum(values)
    return reduced


def map_reduce(text, num_workers=4):
    """Реалізує MapReduce із багатопотоковістю."""
    # Розбиваємо текст на частини
    chunks = split_text(text, num_workers)

    # Паралельно обробляємо Map етап
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        mapped_chunks = executor.map(lambda chunk: map_function(chunk), chunks)

    # Комбінуємо результати мапінгу
    combined_mapped = [pair for sublist in mapped_chunks for pair in sublist]

    # Shuffle і Reduce
    shuffled = shuffle_function(combined_mapped)
    return reduce_function(shuffled)


def split_text(text, num_chunks):
    """Розбиває текст на кількість частин для обробки."""
    lines = text.splitlines()
    chunk_size = max(1, len(lines) // num_chunks)
    return ["\n".join(lines[i:i + chunk_size]) for i in range(0, len(lines), chunk_size)]


def visualize_top_words(word_counts, top_n=10):
    """Візуалізує топ слів за частотою використання."""
    top_words = Counter(word_counts).most_common(top_n)
    words, counts = zip(*top_words)

    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color='skyblue')
    plt.xlabel('Слова', fontsize=14)
    plt.ylabel('Частота', fontsize=14)
    plt.title(f'Топ-{top_n} найчастіше вживаних слів', fontsize=16)
    plt.xticks(rotation=45, fontsize=12)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    url = input(Fore.CYAN + "Введіть URL тексту для аналізу: ").strip()
    try:
        print(Fore.YELLOW + "\nЗавантаження тексту з URL...")
        text = fetch_text_from_url(url)

        # Налаштування параметрів
        num_workers = int(input(Fore.CYAN + "Введіть кількість потоків (за замовчуванням 4): ") or 4)
        top_n = int(input(Fore.CYAN + "Введіть кількість топ-слів для візуалізації (за замовчуванням 10): ") or 10)

        print(Fore.YELLOW + "\nАналіз частоти слів із використанням MapReduce...")
        word_counts = map_reduce(text, num_workers=num_workers)

        # Показуємо загальну кількість слів
        total_words = sum(word_counts.values())
        print(Fore.GREEN + f"\nЗагальна кількість слів у тексті: {total_words}")
        print(Fore.MAGENTA + f"Топ-{top_n} слів за частотою:")

        for word, count in Counter(word_counts).most_common(top_n):
            print(Fore.LIGHTBLUE_EX + f"{word}: {count}")

        # Візуалізація
        print(Fore.YELLOW + "\nВізуалізація результатів...")
        visualize_top_words(word_counts, top_n=top_n)

    except requests.RequestException as e:
        print(Fore.RED + f"Помилка завантаження тексту: {e}")
    except ValueError:
        print(Fore.RED + "Невірний ввід числових параметрів. Будь ласка, введіть ціле число.")
    except Exception as e:
        print(Fore.RED + f"Помилка виконання: {e}")
