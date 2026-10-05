When to read: when applying the language rules to modality, scope, boolean logic, or procedure defects.

## Examples

### Ambiguous modality

Bad:

> You should run the tests before finishing.

If this action is mandatory:

> Run the tests before you finish.

If this action is a default with valid exceptions:

> Run the tests before you finish. You may skip the tests when the required test environment is unavailable. Report the reason when you skip them.

### Undefined discretion

Bad:

> Use a stronger model for complex tasks.

Better:

> Use the default model first. If the default model cannot process the required input format, use a model that supports that format. If no available model supports the format, report the unsupported format and stop.

### Ambiguous reference

Bad:

> Compare the patch with the advisory. If it is incomplete, inspect the source.

Better:

> Compare the patch with the advisory. If the advisory is incomplete, inspect the source.

### Hidden boolean logic

Bad:

> Escalate when the patch affects authentication, authorization, unsafe deserialization, or file writes and the change is externally reachable.

Better:

> Escalate when both of these conditions are true:
>
> - The patch affects authentication, authorization, unsafe deserialization, or file writes.
> - The affected code is externally reachable.

### Unbounded iteration

Bad:

> Continue reviewing until the result is good enough.

Better:

> Run one review pass. Correct the actionable findings. Run one confirmation pass. If actionable findings remain, report them and stop.

### Hidden requirement in a note

Bad:

> Note: Always run the formatter before returning the result.

Better:

> Run the formatter before you return the result.
>
> Note: Formatting prevents unrelated style changes from obscuring the patch.
