# UX Product Specialist

## Objective

Raise the quality of user-facing work by combining product thinking, UX architecture, UI craft, accessibility, responsive behavior, and practical implementation constraints.

This skill is intentionally robust because weak UX review often produces technically correct but mediocre products.

## When to use

Use for any:

- Screen, page, modal, form, dashboard, guided tour, onboarding, pricing, settings, admin UI, flow, empty state, loading state, error state, success state, notification, user-facing copy, or design-system decision.

## When not to use

- Pure backend task with no user-facing impact.
- Internal refactor with no UI behavior change.

## Inputs expected

- User goal.
- Business goal.
- Target users.
- Current screen or flow.
- Brand/design constraints.
- Device targets.
- Existing components/design system.
- Technical constraints.

If inputs are missing, infer carefully from repository context and mark assumptions.

## Process

### 1. Product framing

Answer:

- Who is the user?
- What job are they trying to complete?
- What is the single most important action?
- What decision must the screen make easier?
- What should the user understand in the first 5 seconds?

### 2. Information architecture

Check:

- Is the hierarchy obvious?
- Are related items grouped?
- Are labels user-centered instead of internal jargon?
- Is the order natural?
- Is there unnecessary cognitive load?

### 3. Interaction design

Check:

- Primary action clear.
- Secondary actions visually subordinate.
- Destructive actions protected.
- Cancel/undo/retry paths available where needed.
- Form validation close to the field.
- Error messages explain what happened and how to fix it.
- Loading, empty, success, disabled, and failure states considered.

### 4. Visual design quality

Check:

- Spacing scale is consistent.
- Typography hierarchy is clear.
- Cards/containers have consistent radius, borders, shadows and padding.
- Alignment is intentional.
- Density matches the use case.
- Color is used for meaning, not decoration only.
- The result feels modern without reducing clarity.

### 5. Responsive behavior

Define behavior for:

- Small mobile.
- Large mobile.
- Tablet.
- Desktop.
- Wide desktop.

Check wrapping, overflow, stacked layouts, fixed heights, long text, tables, sidebars, modals and cards.

### 6. Accessibility baseline

Check:

- Keyboard path.
- Focus states.
- Text contrast.
- Non-color indicators.
- Semantic headings.
- Label/input association.
- Touch target size.
- Reduced motion when relevant.
- Screen reader-friendly status/error messages.

### 7. Heuristic review

Evaluate against:

- Visibility of system status.
- Match with real-world language.
- User control and freedom.
- Consistency and standards.
- Error prevention.
- Recognition over recall.
- Flexibility and efficiency.
- Aesthetic and minimalist design.
- Error recognition/recovery.
- Help and documentation where needed.

### 8. Implementation handoff

Produce concrete guidance:

- Component structure.
- State model.
- Layout rules.
- Responsive rules.
- Copy suggestions.
- Acceptance criteria.

## Deliverables

For small UI work:

- UX issues found.
- Specific changes to make.
- States/responsive/accessibility checklist.

For medium/critical UI work:

- UX intent.
- Flow structure.
- IA recommendation.
- UI layout recommendation.
- State inventory.
- Responsive rules.
- Accessibility notes.
- Acceptance criteria.

## Quality criteria

- The main action is obvious.
- The user understands the screen quickly.
- The interface handles edge cases.
- The design works on target screen sizes.
- Accessibility is not an afterthought.
- The design improves clarity, not just aesthetics.
- Recommendations are implementable in the current stack.

## Common risks

- Pretty but unclear UI.
- Desktop-only thinking.
- Missing empty/error/loading states.
- Inconsistent spacing and card sizing.
- Too many competing CTAs.
- Copy written from the system's perspective.
- Accessibility ignored until the end.
- Over-custom UI that breaks the existing design system.


## Written memory rule

For Level 2/3 work, record durable findings, assumptions, risks, and handoff notes in the active task file or the appropriate `docs/ai` file. Do not rely on mental notes.

## Checklist final

- [ ] User goal clear.
- [ ] Primary action clear.
- [ ] IA reviewed.
- [ ] Visual hierarchy reviewed.
- [ ] States reviewed.
- [ ] Responsive behavior reviewed.
- [ ] Accessibility baseline reviewed.
- [ ] Copy reviewed.
- [ ] Acceptance criteria defined.
