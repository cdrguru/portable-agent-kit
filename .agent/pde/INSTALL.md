# PDE Installer Guide

## How to Port This System

The `.pde/` folder is a self-contained "AI Operating System Kernel". To use it in another project:

1. **Copy**: `cp -r .pde/ /path/to/new/project/`
2. **Configure**: Edit `.pde/MANIFEST.md` to update the "North Star" for that specific project context.
3. **Clean State**: Run `echo "# Tasks" > .pde/state/active_tasks.md` to clear the legacy state.

## Integration

To make the agents aware of your project code, refer to them in your main `CLAUDE.md` or system prompt:

```markdown
## AI OS Integration
This project uses the PDE Engine.
- Constitution: `.pde/MANIFEST.md`
- Agents: `.pde/agents/`
```
