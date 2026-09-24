# Decodificador de Instruções RISC-V — Etapa 1

## Contexto

Este projeto corresponde à primeira etapa de um decodificador de instruções RISC-V. O objetivo é extrair de cada instrução, de forma confiável, seu formato, mnemônico, registradores envolvidos e valores imediatos.

A decodificação correta é importante para a próxima etapa do projeto, que será responsável pela identificação de conflitos (*hazards*) de dados e de controle em um pipeline RISC-V.

## Funcionamento

O programa recebe um arquivo contendo instruções RISC-V em linguagem de máquina e realiza a decodificação de cada instrução.

As instruções podem ser fornecidas em hexadecimal ou binário. O programa identifica automaticamente o formato da entrada, ignora linhas vazias, comentários e o prefixo `0x`, e atribui um endereço (`PC`) para cada instrução a partir de um endereço-base configurável.

## Classificação e identificação

O projeto classifica as instruções nos seis formatos da arquitetura RISC-V:

* R
* I
* S
* B
* U
* J

Além da classificação, o programa identifica o mnemônico da instrução utilizando a combinação de `opcode`, `funct3` e `funct7`.

Instruções não reconhecidas são identificadas como inválidas e não interrompem o processamento das demais instruções do arquivo.

## Extração dos campos

Para cada instrução válida, o programa extrai somente os campos existentes de acordo com seu formato.

São identificados campos como:

* `rd`
* `rs1`
* `rs2`
* `funct3`
* `funct7`
* `imm`

Os valores imediatos são reconstruídos de acordo com o formato da instrução, incluindo os casos em que os bits do imediato estão distribuídos em diferentes posições, como nos formatos B e J.

Quando necessário, é aplicada a extensão de sinal para representar corretamente valores negativos.

## Saída

O programa apresenta uma listagem contendo:

* Endereço da instrução;
* Palavra original;
* Formato;
* Mnemônico;
* Campos extraídos;
* Instrução em Assembly.

Os registradores são apresentados utilizando seus nomes ABI, como `s0`, `sp`, `a0`, `t0`, entre outros.

Para instruções de desvio e salto, o programa calcula o endereço absoluto de destino.

Também são reconhecidas algumas pseudoinstruções comuns, como:

```text
addi x0, x0, 0 → nop
jalr x0, 0(x1) → ret
```

## Formatos de instrução

O projeto utiliza os campos correspondentes a cada formato da arquitetura RISC-V:

| Formato | rd  | rs1 | rs2 | funct3 | funct7 | Imediato |
| ------- | --- | --- | --- | ------ | ------ | -------- |
| Tipo R  | sim | sim | sim | sim    | sim    | —        |
| Tipo I  | sim | sim | —   | sim    | —      | 12 bits  |
| Tipo S  | —   | sim | sim | sim    | —      | 12 bits  |
| Tipo B  | —   | sim | sim | sim    | —      | 13 bits  |
| Tipo U  | sim | —   | —   | —      | —      | 32 bits  |
| Tipo J  | sim | —   | —   | —      | —      | 21 bits  |

## Exemplos de decodificação

### `0x00500413`

```text
Formato: I
Mnemônico: addi
rd = 8
rs1 = 0
imm = 5
f3 = 0

Assembly: addi s0, zero, 5
```

### `0x00C58633`

```text
Formato: R
Mnemônico: add
rd = 12
rs1 = 11
rs2 = 12
f3 = 0
f7 = 0

Assembly: add a2, a1, a2
```

### `0x0064A423`

```text
Formato: S
Mnemônico: sw
rs1 = 9
rs2 = 6
imm = 8

Assembly: sw t1, 8(s1)
```

### `0xFE628CE3`

```text
Formato: B
Mnemônico: beq
rs1 = 5
rs2 = 6
imm = -8

Assembly: beq t0, t1, <PC-8>
```

No formato B, o projeto não interpreta os bits `11` a `7` como `rd`, pois esse formato não possui esse campo. Esses bits fazem parte da composição do imediato.

## Relatório estatístico

Ao final do processamento, o projeto apresenta um relatório contendo:

* Quantidade de instruções de cada formato;
* Percentual de cada formato em relação ao total de instruções válidas;
* CPI médio estimado do programa.

O CPI médio é calculado utilizando uma média aritmética ponderada, considerando o CPI associado a cada formato de instrução.

A tabela utilizada pelo projeto é:

| Formato | CPI |
| ------- | --: |
| R       | 1,0 |
| I       | 1,0 |
| S       | 2,0 |
| B       | 3,0 |
| U       | 1,0 |
| J       | 2,0 |

## Validação

O projeto pode ser validado utilizando códigos de máquina gerados a partir de programas RISC-V ou por meio de simuladores da arquitetura.

Os testes contemplam:

* Entrada em hexadecimal;
* Entrada em binário;
* Os seis formatos de instrução;
* Identificação de mnemônicos;
* Extração dos campos de cada formato;
* Imediatos positivos e negativos;
* Imediatos dos formatos B e J;
* Desvios com deslocamento negativo;
* Pseudoinstruções;
* Cálculo do endereço de destino de desvios e saltos;
* Relatório estatístico e CPI médio.

## Etapa 2

A próxima etapa do projeto utilizará as instruções já decodificadas para identificar conflitos de dados e de controle em um pipeline RISC-V de cinco estágios.

A análise incluirá o tipo de conflito, as instruções envolvidas e a quantidade de ciclos de parada necessários.
