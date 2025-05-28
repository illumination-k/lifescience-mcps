---
applyTo: "**/*.py"
mode: agent
---

あなたはソフトウェアエンジニアで、Pythonを用いてソフトウェア開発をしています。

## Python Version

このプロジェクトでは、Python 3.12以降のバージョンを使用します。

## Type Annotations

Pythonでは、型アノテーションを使用してコードの可読性と保守性を向上させることが推奨されています。
型アノテーションは、関数の引数や戻り値の型を明示的に指定することで、コードの意図を明確にします。
必ず型を指定してください。

### Rules

- `list`, `dict`, `set`, `tuple`などのコレクション型は、具体的な要素の型を指定することが推奨されます。
- `Union`は`|`を使用して表現します。
- `Optional`は`| None`を使用して表現します。

### 使用例

```python
def sum(numbers: list[int]) -> int:
    return sum(numbers)

def get_user_name(user: dict[str, str]) -> str | None:
    return user.get("name", "Unknown")
```

## Testing

コードを実装した場合、テストを必ず書く必要があります。
テストでは、mockは基本的に使用しないでください。mockを使用せざるを得ない場合は、判断を仰いでください。
テストでは、TDDの原則に従い、Red-Green-Refactorのサイクルを守ってください。

### 使用ライブラリ

- `pytest`

### テストの実行

テストは、コードの品質を保つために重要な役割を果たします。以下の手順に従って、テストを実行してください。

```bash
mise r test
```
