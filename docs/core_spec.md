# Core Specification (v0.1)

This document defines the formal core boundary used by all language frontends.

## Scope

- Frontends parse language-specific concrete syntax into a shared Core AST.
- Core AST is wrapped in a typed IR container `CoreIRProgram`.
- Code generation and execution consume this typed core.

## Core Object

`CoreIRProgram` fields:

- `ast: Program` (required)
- `source_language: str` (required)
- `core_version: str` (default `0.1`)
- `frontend_metadata: dict` (optional metadata)

## Core Grammar (Minimal)

The current parser supports a richer grammar than shown here. This minimal
subset captures the main contract:

```text
Program      ::= Statement*
Statement    ::= LetDecl | Assign | IfStmt | ForStmt | WhileStmt | ExprStmt
LetDecl      ::= "LET" Identifier "=" Expr
Assign       ::= Target "=" Expr
IfStmt       ::= "COND_IF" Expr ":" Block ("COND_ELIF" Expr ":" Block)* ("COND_ELSE" ":" Block)?
ForStmt      ::= "LOOP_FOR" Target "IN" Expr ":" Block
WhileStmt    ::= "LOOP_WHILE" Expr ":" Block
ExprStmt     ::= Expr
Block        ::= INDENT Statement* DEDENT
Expr         ::= Literal | Identifier | Call | Binary | Unary | Compare | Collection
```

Notes:

- `LET`, `COND_IF`, `LOOP_FOR`, etc. are semantic concepts, not literal source words.
- Concrete keywords (`let`, `soit`, etc.) map to concepts in frontend processing.

## Typing/Validation Rules

Core validation currently enforces:

1. `ast` must be a `Program`.
2. `source_language` must be a non-empty string.

Planned extension:

- statement/expression sort checks
- typed annotation consistency checks
- lowering invariants for restricted subsets

## Forward-Only Property

The system guarantees compilation direction:

`CS_lang -> CoreAST -> CoreIRProgram -> Python`

It does not guarantee reconstruction of the original source form from core.
