import os
import requests
from dotenv import load_dotenv
from itertools import count
from terminaltables import AsciiTable


def print_table_data(data, title=""):
    table_data = [
        [
            "Language",
            "Vacancies found",
            "Vacancies processed",
            "Average salary"
        ]
    ]

    for key, value in data.items():
        line = [key]
        line.extend(value.values())
        table_data.append(line)

    table = AsciiTable(table_data, title)
    print(table.table)


def predict_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        return None
    elif salary_from and salary_to:
        return (salary_to + salary_from) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8


def get_vacancies_superjob(api_token, language="", page=0):
    headers = {
        "X-Api-App-Id": f"{api_token}",
    }

    params = {
        "keyword": f"{language}",
        "town": 4,
        "page": page,
    }

    url = "https://api.superjob.ru/2.0/vacancies/"

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def get_vacancies_information_sj(api_token, languages):
    vacancies_info = {}

    for language in languages:
        salaries = []
        found = 0
        vacancies_all = []
        for page in count(0):
            vacancies = get_vacancies_superjob(
                api_token,
                language=language,
                page=page
            )
            vacancies_all.extend(vacancies.get("objects"))
            if not vacancies.get("more"):
                found = vacancies.get("total")
                break

        for vacancy in vacancies_all:
            salary = predict_rub_salary_for_superjob(vacancy)
            if salary:
                salaries.append(salary)
        predicted_salary = 0
        if salaries:
            predicted_salary = int(sum(salaries) / len(salaries))
        info = {
            "vacancies_found": found,
            "vacancies_processed": len(salaries),
            "average_salary": predicted_salary,
        }
        vacancies_info[language] = info

    return vacancies_info


def predict_rub_salary_for_superjob(vacancy):
    salary_from = vacancy.get("payment_from")
    salary_to = vacancy.get("payment_to")

    return predict_salary(salary_from, salary_to)


def get_vacancies(language="", page=0):

    headers = {
        "User-Agent": "MyApp / 1.0(my - app - feedback @ example.com)"
    }

    params = {
        "text": f"программист {language}",
        "id": 1,
        "period": 30,
        "per_page": 20,
        "page": page,
    }

    response = requests.get(
        "https://api.hh.ru/vacancies",
        headers=headers,
        params=params
    )

    response.raise_for_status()
    return response.json()


def get_vacancies_count(languages):

    number_of_vacancies = {}

    for language in languages:
        params = {
            "text": f"программист {language}",
            "id": 1,
            "period": 30,
        }
        response = requests.get("https://api.hh.ru/vacancies", params=params)
        response.raise_for_status()
        number_of_vacancies[language] = response.json().get("found")

    return number_of_vacancies


def get_salaries_range(vacancies):

    salaries = []

    for vacancy in vacancies:
        salaries.append(vacancy.get("salary"))
    return salaries


def predict_rub_salary_for_hh(vacancy):
    if not vacancy:
        return None
    salary = vacancy.get("salary")

    if not salary or salary.get("currency") != "RUR":
        return None
    return predict_salary(
        salary_from=salary.get("from"),
        salary_to=salary.get("to"),
    )


def get_vacancies_information(languages):
    vacancies_information = {}
    for language in languages:
        found = 0
        salaries = []
        vacancies_all = []
        for page in count(0):
            try:
                vacancies = get_vacancies(language, page=page)

                vacancies_all.extend(vacancies.get("items"))
            except requests.exceptions.HTTPError:
                pass
            if page >= 10:
                found = vacancies.get("found")
                break

        for vacancy in vacancies_all:
            salary = predict_rub_salary_for_hh(vacancy)
            if salary:
                salaries.append(salary)

        predicted_salary = 0
        if salaries:
            predicted_salary = int(sum(salaries) / len(salaries))

        info = {
            "vacancies_found": found,
            "vacancies_processed": len(salaries),
            "average_salary": predicted_salary,
        }
        vacancies_information[language] = info

    return vacancies_information


def main():
    load_dotenv()
    super_job_token = os.environ['SUPER_JOB_TOKEN']

    languages = [
        "Python",
        "Java",
        "JavaScript",
        "Ruby",
        "PHP",
        "Swift",
        "Go",
        "C#",
        "C++",
        "C",
    ]

    print_table_data(get_vacancies_information(languages), title="HH Moscow")

    print_table_data(
        get_vacancies_information_sj(
            super_job_token,
            languages
        ),
        title="SJ Moscow",
    )


if __name__ == "__main__":
    main()
