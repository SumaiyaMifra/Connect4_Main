import pygame
import button
from subprocess import call




pygame.init()

screen = pygame.display.set_mode((800, 450))
boardImg = pygame.image.load('connect.png')
screen.blit(boardImg, (0, 0))

pygame.display.set_caption('Connect4')

# Load button images
start_img = pygame.image.load('start_btn.png').convert_alpha()
exit_img = pygame.image.load('exit_btn.png').convert_alpha()

# Create button instances
start_button = button.Button(100, 250, start_img, 0.45)
exit_button = button.Button(100, 350, exit_img, 0.5)



# Game loop
run = True
while run:
    screen.blit(boardImg, (0, 0))  # Redraw the background image

    if start_button.draw(screen):
        print('START')
        call(["python", "newtrial.py"])



    if exit_button.draw(screen):
        print('EXIT')
        pygame.quit()



    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False


    pygame.display.update()

pygame.quit()
