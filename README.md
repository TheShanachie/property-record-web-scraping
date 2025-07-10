Selenium v4.33.0


Create a pydantic model, given the later json-schema. Read and understand the following rules, which you should use while converting to a pydantic model. The rules are as follows:

Pydantic Model Requirements

All fields required - No defaults, but use Optional[str] for whitespace conversion

No extra fields - extra = "forbid" in Config

Snake_case variables with original JSON names as Field(alias="")

Allow both naming styles - allow_population_by_field_name = True

Convert whitespace-only strings to None - @validator('*', pre=True) with not v.strip()

Separate classes for nested objects

Proper imports - List, Optional, validator

Proper use of validators - Note that the pydantic member 'validator' is depreciated.

Lastly, the following json-schema for conversion is as such:

```

```