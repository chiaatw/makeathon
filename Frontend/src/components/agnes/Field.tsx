import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ReactNode } from "react";

export const Field = ({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: ReactNode;
}) => (
  <div className="space-y-1.5">
    <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
      {label}
    </Label>
    {children}
    {hint && <p className="text-xs text-muted-foreground/80">{hint}</p>}
  </div>
);

export const SelectField = ({
  label,
  value,
  onChange,
  options,
  placeholder,
  hint,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: readonly string[];
  placeholder?: string;
  hint?: string;
}) => (
  <Field label={label} hint={hint}>
    <Select value={value || undefined} onValueChange={onChange}>
      <SelectTrigger className="h-11 bg-card border-border/80 hover:border-primary/40 ease-smooth transition-colors">
        <SelectValue
          placeholder={placeholder ?? `Select ${label.toLowerCase()}`}
        />
      </SelectTrigger>
      <SelectContent>
        {options.map((o) => (
          <SelectItem key={o} value={o}>
            {o}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  </Field>
);
