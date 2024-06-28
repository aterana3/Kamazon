**Idea del Proyecto:**

Kamazon es un proyecto de programación diseñado para el aprendizaje universitario, inspirado en la idea de negocio de Amazon. El proyecto se enfoca en la creación de una aplicación web que permita a los usuarios registrados comprar productos de diversas categorías, así como a los vendedores publicar productos y gestionar sus ventas. Además, Kamazon contará con un sistema de compras físicas mediante un carro inteligente que, a través de una cámara y IA, analizará los productos que se están adquiriendo y los añadirá al carrito de compras.

---
**Colaboradores:**
- [Christian Pin](https://github.com/Crisblue1324) 
- [Roger Cornejo](https://github.com/Rcornejom06/)
---
**Tecnologias Utilizadas:**
- Python
- Django
- HTML
- Tailwind CSS
- JavaScript
---
**Instalacion:**
1. Clonar el repositorio
```bash
git clone https://github.com/aterana3/Kamazon-Proyecto-5to-semestre.git
```
2. Instalar las dependencias
```bash
pip install -r dependencias.txt
```
3. Crear migraciones
```bash
python manage.py makemigrations / python manage.py makemigrations <app_name>
python manage.py migrate
```
4. Crear tabla cache
```bash
python manage.py createcachetable
```
5. Crear superusuario
```bash
python manage.py createsuperuser
```
5. Correr el servidor
```bash
python manage.py runserver 0.0.0.0:8000
```