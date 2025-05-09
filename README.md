# Kafka Project

## Описание проекта

Это полнофункциональное приложение, демонстрирующее использование Kafka для коммуникации между микросервисами, с бэкендом на FastAPI и фронтендом на React.

## Инициализация данных

### База данных

База данных инициализируется автоматически при первом запуске приложения. Данные берутся из двух источников:

1. **Файл .env** - содержит настройки подключения к базе данных и данные для создания администратора:
   - Имя пользователя администратора
   - Пароль администратора


2. **Файл /kafka/back/data/users.json** - содержит данные о:
   - Отделах компании
   - Сотрудниках с различными ролями
   - Рабочих данных сотрудников

### Пользователи и роли

По умолчанию в системе создается один администратор с данными из файла .env. Дополнительные пользователи и отделы загружаются из файла users.json.

## Интерфейс приложения

Интерфейс и доступные функции приложения зависят от роли пользователя:

### Администратор
- Полный доступ ко всем функциям
- Управление пользователями и отделами
- Изменение ролей и назначений отделов
- Просмотр и редактирование рабочих данных всех сотрудников

### Руководитель отдела
- Управление сотрудниками своего отдела
- Просмотр рабочих данных сотрудников отдела
- Обновление рабочих данных сотрудников отдела

### Обычный пользователь
- Просмотр своего профиля
- Просмотр своих рабочих данных
- Ограниченный доступ к другим функциям

## Технические особенности

- Аутентификация через JWT токены
- Микросервисная архитектура с использованием Kafka
- Асинхронное взаимодействие между сервисами
- Реактивный пользовательский интерфейс

## Overview

The application provides a user management system with different roles and departments. The interface and available features depend on the user's role.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone &lt;repository-url&gt;
   cd freelance/kafka
   ```