def gerar_bootloader():
    import os

    nome_os = input("Nome do sistema operacional: ")
    desc_os = input("Descrição do sistema operacional: ")
    prompt = input("Prompt do terminal: ")
    comandos = []
    while True:
        cmd = input("Digite um comando (ou deixe vazio para terminar): ")
        if cmd == "":
            break
        resposta = input(f"Resposta para '{cmd}': ")
        comandos.append((cmd, resposta))

    #Criar pasta do sistema
    if not os.path.exists(nome_os):
        os.makedirs(nome_os)

    ### STAGE 1 ###
    stage1 = []
    stage1.append("org 0x7c00")
    stage1.append("bits 16\n")

    stage1.append("start:")
    stage1.append("    mov ah, 0x00")
    stage1.append("    mov al, 0x03")
    stage1.append("    int 0x10")

    stage1.append("    mov si, msg")
    stage1.append("print_msg:")
    stage1.append("    lodsb")
    stage1.append("    or al, al")
    stage1.append("    jz load_stage2")
    stage1.append("    call print_char")
    stage1.append("    jmp print_msg")

    stage1.append("load_stage2:")
    stage1.append("    mov ah, 0x02")
    stage1.append("    mov al, 0x01")
    stage1.append("    mov ch, 0x00")
    stage1.append("    mov cl, 0x02")
    stage1.append("    mov dh, 0x00")
    stage1.append("    mov dl, 0x00")
    stage1.append("    mov bx, 0x8000")
    stage1.append("    int 0x13")
    stage1.append("    jmp 0x0000:0x8000")

    stage1.append("print_char:")
    stage1.append("    mov ah, 0x0E")
    stage1.append("    int 0x10")
    stage1.append("    ret")

    stage1.append("msg db 'Carregando stage 2...', 0")
    stage1.append("times 510-($-$$) db 0")
    stage1.append("dw 0xAA55")

    with open(f"{nome_os}/{nome_os}_stage1.asm", "w") as f:
        f.write("\n".join(stage1))

    ### STAGE 2 ###
    asm = []

    asm.append("org 0x8000")
    asm.append("bits 16\n")

    asm.append("start:")
    asm.append("    mov ah, 0x00")
    asm.append("    mov al, 0x03")
    asm.append("    int 0x10")

    asm.append("    mov si, os_name")
    asm.append("print_os_name:")
    asm.append("    lodsb")
    asm.append("    or al, al")
    asm.append("    jz print_os_desc")
    asm.append("    call print_char")
    asm.append("    jmp print_os_name")

    asm.append("print_os_desc:")
    asm.append("    mov al, 0x0D")
    asm.append("    call print_char")
    asm.append("    mov al, 0x0A")
    asm.append("    call print_char")
    asm.append("    mov si, os_desc")
    asm.append("print_os_desc_loop:")
    asm.append("    lodsb")
    asm.append("    or al, al")
    asm.append("    jz print_prompt")
    asm.append("    call print_char")
    asm.append("    jmp print_os_desc_loop")

    asm.append("print_prompt:")
    asm.append("    mov si, prompt")
    asm.append("print_prompt_loop:")
    asm.append("    lodsb")
    asm.append("    or al, al")
    asm.append("    jz read_input")
    asm.append("    call print_char")
    asm.append("    jmp print_prompt_loop")

    asm.append("read_input:")
    asm.append("    mov si, 0")
    asm.append("read_loop:")
    asm.append("    mov ah, 0x00")
    asm.append("    int 0x16")
    asm.append("    cmp al, 0x0D")
    asm.append("    je process_command")
    asm.append("    cmp al, 0x08")
    asm.append("    je backspace")
    asm.append("    mov [input_buffer + si], al")
    asm.append("    inc si")
    asm.append("    call print_char")
    asm.append("    jmp read_loop")

    asm.append("backspace:")
    asm.append("    cmp si, 0")
    asm.append("    je read_loop")
    asm.append("    dec si")
    asm.append("    mov ah, 0x0E")
    asm.append("    mov al, 0x08")
    asm.append("    int 0x10")
    asm.append("    mov al, ' '")
    asm.append("    int 0x10")
    asm.append("    mov al, 0x08")
    asm.append("    int 0x10")
    asm.append("    jmp read_loop")

    asm.append("process_command:")
    asm.append("    mov byte [input_buffer + si], 0")
    asm.append("    mov ah, 0x0E")
    asm.append("    mov al, 0x0D")
    asm.append("    int 0x10")
    asm.append("    mov al, 0x0A")
    asm.append("    int 0x10")
    asm.append("    mov si, input_buffer")

    for i, (cmd, resp) in enumerate(comandos):
        asm.append(f"    mov di, cmd_{i}")
        asm.append("    call str_compare")
        asm.append("    cmp al, 1")
        asm.append(f"    je print_resp_{i}")

    asm.append("    mov si, unknown_cmd")
    asm.append("    call print_string")
    asm.append("    jmp print_prompt")

    for i, (cmd, resp) in enumerate(comandos):
        asm.append(f"print_resp_{i}:")
        asm.append(f"    mov si, resp_{i}")
        asm.append("    call print_string")
        asm.append("    jmp print_prompt")

    asm.append("print_char:")
    asm.append("    mov ah, 0x0E")
    asm.append("    int 0x10")
    asm.append("    ret")

    asm.append("print_string:")
    asm.append("    lodsb")
    asm.append("    or al, al")
    asm.append("    jz .done")
    asm.append("    call print_char")
    asm.append("    jmp print_string")
    asm.append(".done:")
    asm.append("    mov al, 0x0D")
    asm.append("    call print_char")
    asm.append("    mov al, 0x0A")
    asm.append("    call print_char")
    asm.append("    ret")

    asm.append("str_compare:")
    asm.append("    push si")
    asm.append("    push di")
    asm.append(".loop:")
    asm.append("    mov al, [di]")
    asm.append("    mov bl, [si]")
    asm.append("    cmp al, bl")
    asm.append("    jne .no")
    asm.append("    test al, al")
    asm.append("    je .yes")
    asm.append("    inc si")
    asm.append("    inc di")
    asm.append("    jmp .loop")
    asm.append(".yes:")
    asm.append("    mov al, 1")
    asm.append("    pop di")
    asm.append("    pop si")
    asm.append("    ret")
    asm.append(".no:")
    asm.append("    mov al, 0")
    asm.append("    pop di")
    asm.append("    pop si")
    asm.append("    ret")

    asm.append("input_buffer times 128 db 0")
    asm.append(f"os_name db '{nome_os}',0")
    asm.append(f"os_desc db '{desc_os}',0")
    asm.append("unknown_cmd db 'Comando desconhecido',0")
    asm.append(f"prompt db '{prompt}',0")
    for i, (cmd, resp) in enumerate(comandos):
        asm.append(f"cmd_{i} db '{cmd}',0")
        asm.append(f"resp_{i} db '{resp}',0")

    with open(f"{nome_os}/{nome_os}_stage2.asm", "w") as f:
        f.write("\n".join(asm))

    import platform

    # Detectar sistema operacional
    sistema = platform.system()

    # 🛠️ Criar script de compilação .bat ou .sh conforme o sistema
    if sistema == "Windows":
        compila = [
            "@echo off",
            f"nasm -f bin {nome_os}_stage1.asm -o stage1.bin",
            f"nasm -f bin {nome_os}_stage2.asm -o stage2.bin",
            f"copy /b stage1.bin+stage2.bin boot.img",
            'echo boot.img gerado com sucesso!',
            "pause"
        ]
        script_path = f"{nome_os}/compila.bat"
    else:
        compila = [
            "#!/bin/bash",
            f"nasm -f bin {nome_os}_stage1.asm -o stage1.bin",
            f"nasm -f bin {nome_os}_stage2.asm -o stage2.bin",
            f"cat stage1.bin stage2.bin > boot.img",
            'echo "boot.img gerado com sucesso!"'
        ]
        script_path = f"{nome_os}/compila.sh"

    # Salvar o script
    with open(script_path, "w") as f:
        f.write("\n".join(compila))

    if sistema != "Windows":
        os.chmod(script_path, 0o755)

    print(f"\nPasta '{nome_os}' criada com sucesso!")
    print(f"Arquivos '{nome_os}_stage1.asm', '{nome_os}_stage2.asm' e script de compilação gerados.")
    if sistema == "Windows":
        print(f"Vá até a pasta '{nome_os}' e execute 'compila.bat' para compilar tudo.")
    else:
        print(f"Vá até a pasta '{nome_os}' e execute './compila.sh' para compilar tudo.")
    print("Bootloader gerado com sucesso!")


# Executar CLI
if __name__ == "__main__":
    gerar_bootloader()
