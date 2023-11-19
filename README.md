# Vacancies parser
A set of scripts to parse vacancies on websites HeadHunter and SuperJob and to output them in an easy readable manner.

### Environment variables
- SUPER_JOB_TOKEN

1. Put `.env` file near `main.py`.
2. `.env` contains text data without quotes.

## Table print

Can be done by launching

```
python3 main.py
```

Prints information on vacations on two sites, and calculates information grouped by some popular programming languages. 

### get_vacancies_information

Obtains information on programming related vacancies on HeadHunter.

### get_vacancies_information_sj

Obtains information on programming related vacancies on SuperJob. Requires SuperJob API token.