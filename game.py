import pygame
import random
import sys
import os
import json

# Inicia o Pygame
pygame.init()

# Constantes da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_HEIGHT = 50
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Janela do jogo
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Astro Jump")
clock = pygame.time.Clock()

# background
background = pygame.image.load(os.path.join('img', 'spacewallpaper.png'))
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Função para carregar pontuações
def load_scores():
    try:
        with open('scores.json', 'r') as f:
            return json.load(f)
    except:
        return []

# Função para salvar pontuações
def save_scores(scores):
    with open('scores.json', 'w') as f:
        json.dump(scores, f)

# Função para adicionar nova pontuação
def add_score(name, score):
    scores = load_scores()
    scores.append({'name': name, 'score': score})
    scores.sort(key=lambda x: x['score'], reverse=True)
    scores = scores[:5]  # Mantém apenas as top 4 pontuações
    save_scores(scores)

# Classe do botão
class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 36)
        
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Classe do astronauta
class Astronaut:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - 60
        self.width = 40
        self.height = 60
        self.jumping = False
        self.jump_velocity = 0
        self.gravity = 0.7
        self.jump_power = -12

        # Carrega as imagens do astronauta
        self.image_right = pygame.image.load(os.path.join('img', 'astro_direita.png'))
        self.image_right = pygame.transform.scale(self.image_right, (self.width, self.height))
        self.image_left = pygame.image.load(os.path.join('img', 'astro_esquerda.png'))
        self.image_left = pygame.transform.scale(self.image_left, (self.width, self.height))
        self.image_still = pygame.image.load(os.path.join('img', 'astro_parado.png'))
        self.image_still = pygame.transform.scale(self.image_still, (self.width, self.height))
        self.image_crouch = pygame.image.load(os.path.join('img', 'astro_agachado.png'))
        self.image_crouch = pygame.transform.scale(self.image_crouch, (self.width, self.height))
        self.image_jump = pygame.image.load(os.path.join('img', 'astro_cima.png'))
        self.image_jump = pygame.transform.scale(self.image_jump, (self.width, self.height))
        
        # Variáveis para animação
        self.current_image = self.image_right
        self.animation_timer = 0
        self.animation_speed = 0.05  # Velocidade da animação mais suave
        self.animation_state = 0  # 0: direita, 1: parado, 2: esquerda, 3: parado
        self.jump_animation_timer = 0
        self.jump_animation_speed = 0.1  # Velocidade da animação do pulo
        self.jump_animation_state = 0  # 0: agachado, 1: pulando

    def jump(self):
        if not self.jumping:
            self.jump_velocity = self.jump_power
            self.jumping = True
            self.jump_animation_state = 0
            self.jump_animation_timer = 0
            self.current_image = self.image_crouch

    def update(self):
        if self.jumping:
            self.y += self.jump_velocity
            self.jump_velocity += self.gravity

            # Atualiza a animação do pulo
            self.jump_animation_timer += self.jump_animation_speed
            if self.jump_animation_timer >= 1:
                self.jump_animation_timer = 0
                if self.jump_animation_state == 0:
                    self.current_image = self.image_jump
                    self.jump_animation_state = 1

            if self.y >= SCREEN_HEIGHT - GROUND_HEIGHT - self.height:
                self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
                self.jumping = False
                self.jump_velocity = 0
                self.animation_state = 0  # Reseta para a animação de corrida
                self.animation_timer = 0  # Reseta o timer da animação
                self.current_image = self.image_right  # Força a primeira frame da corrida
        else:
            # Atualiza a animação de corrida
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.animation_state = (self.animation_state + 1) % 4
                if self.animation_state == 0:
                    self.current_image = self.image_right
                elif self.animation_state == 1:
                    self.current_image = self.image_still
                elif self.animation_state == 2:
                    self.current_image = self.image_left
                else:
                    self.current_image = self.image_still

    def draw(self):
        screen.blit(self.current_image, (self.x, self.y))

# Classe do satélite (obstáculo)
class Satellite:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.x = SCREEN_WIDTH
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        self.speed = 8

        # Imagem do satélite
        image_path = os.path.join('img', 'satelite.png')
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def update(self):
        self.x -= self.speed

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

# Classe para input de texto
class TextInput:
    def __init__(self, x, y, width, height, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.font = pygame.font.Font(None, font_size)
        self.active = False
        self.color = WHITE

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 10:  # Limita o nome a 10 caracteres
                    self.text += event.unicode
        return False

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect, 2)
        text_surface = self.font.render(self.text, True, self.color)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

# Tela de input do nome
def show_name_input():
    text_input = TextInput(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 40)
    font = pygame.font.Font(None, 36)
    instruction = font.render("Digite seu nome (máx 10 caracteres):", True, WHITE)
    
    while True:
        screen.blit(background, (0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if text_input.handle_event(event):
                return text_input.text

        screen.blit(instruction, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50))
        text_input.draw()
        
        pygame.display.flip()
        clock.tick(FPS)

# Tela de pontuações
def show_scores():
    back_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50, "Voltar", BLUE)
    scores = load_scores()
    
    while True:
        screen.blit(background, (0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.is_clicked(event.pos):
                    return

        # Título
        font = pygame.font.Font(None, 74)
        title = font.render("Top 4 Pontuações", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - 200, 50))

        pygame.draw.rect(screen, pygame.Color(200,200,200), (200,150,400,150))
        # Lista de pontuações
        font = pygame.font.Font(None, 36)
        for i, score in enumerate(scores):
            text = font.render(f"{i+1}. {score['name']}: {score['score']}", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - 100, 150 + i * 40))

        back_button.draw()
        pygame.display.flip()
        clock.tick(FPS)

# Tela do menu principal
def show_menu():
    start_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50, 200, 50, "Iniciar Jogo", BLUE)
    instructions_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 50, "Instruções", BLUE)
    scores_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 150, 200, 50, "Pontuações", BLUE)
    back_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50, "Voltar", BLUE)
    showing_instructions = False

    while True:
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if showing_instructions:
                    if back_button.is_clicked(event.pos):
                        showing_instructions = False
                else:
                    if start_button.is_clicked(event.pos):
                        return "start"
                    if instructions_button.is_clicked(event.pos):
                        showing_instructions = True
                    if scores_button.is_clicked(event.pos):
                        show_scores()

        if showing_instructions:
            # Desenha as instruções
            font = pygame.font.Font(None, 36)
            instructions = [
                "Como jogar:",
                "Pressione ESPAÇO para o astronauta pular",
                "Evite os satélites",
                "Você ganha pontos ao passar por cada satélite",
                "Fim de jogo ao colidir com um satélite",
                "Pressione ESPAÇO para reiniciar após perder"
            ]
            for i, line in enumerate(instructions):
                text = font.render(line, True, WHITE)
                screen.blit(text, (50, 50 + i * 40))
            
            back_button.draw()
        else:
            # Desenha o menu principal
            start_button.draw()
            instructions_button.draw()
            scores_button.draw()
            font = pygame.font.Font(None, 74)
            title = font.render("Astro Jump", True, WHITE)
            screen.blit(title, (SCREEN_WIDTH//2 - 150, 50))

        pygame.display.flip()
        clock.tick(FPS)

# Função principal do jogo
def game_loop():
    astronaut = Astronaut()
    satellites = []
    score = 0
    game_over = False
    font = pygame.font.Font(None, 36)
    player_name = show_name_input()  # Pede o nome do jogador antes de começar

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over:
                        add_score(player_name, score)  # Salva a pontuação
                        return  # Volta ao menu
                    else:
                        astronaut.jump()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_over:
                    add_score(player_name, score)  # Salva a pontuação
                    return  # Volta ao menu

        if not game_over:
            astronaut.update()

            # Gera novos satélites
            if len(satellites) == 0 or satellites[-1].x < SCREEN_WIDTH - random.randint(200, 400):
                if random.random() < 0.03:  # Aumenta a chance de spawn
                    # Chance de spawnar dois satélites juntos
                    if random.random() < 0.3:  # 30% de chance de spawnar dois
                        satellites.append(Satellite())
                        second_satellite = Satellite()
                        second_satellite.x = SCREEN_WIDTH + 50  # Espaçamento entre os satélites
                        satellites.append(second_satellite)
                    else:
                        satellites.append(Satellite())

            for satellite in satellites[:]:
                satellite.update()
                if satellite.x + satellite.width < 0:
                    satellites.remove(satellite)
                    score += 1

            # Verifica colisão
            for satellite in satellites:
                if (astronaut.x < satellite.x + satellite.width and
                    astronaut.x + astronaut.width > satellite.x and
                    astronaut.y < satellite.y + satellite.height and
                    astronaut.y + astronaut.height > satellite.y):
                    game_over = True

        # Tela do jogo
        screen.blit(background, (0, 0))  # Desenha o background

        # Chão
        pygame.draw.rect(screen, GRAY, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

        # Astronauta
        astronaut.draw()

        # Satélites
        for satellite in satellites:
            satellite.draw()

        # Pontuação
        score_text = font.render(f"Pontuação: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if game_over:
            game_over_text = font.render("Fim de Jogo! Clique para voltar ao menu", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2))

        pygame.display.flip()
        clock.tick(FPS)

# Loop principal
def main():
    while True:
        menu_action = show_menu()

        if menu_action == "start":
            game_loop()
        elif menu_action == "instructions":
            show_menu()
        elif menu_action == "menu":
            continue

if __name__ == "__main__":
    main()