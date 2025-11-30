"use client";

import { Building2 } from "lucide-react";
import { useState, useMemo } from "react";

import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Button } from "@/components/ui/button";
import { companies } from "@/data/companies";

interface SearchCommandProps {
  value?: string;
  onChange?: (value: string) => void;
  onCompanySelect?: (company: { name: string; sector: string }) => void;
  onManualSearch?: () => void;
}

export function SearchCommand({
  value: controlledValue,
  onChange,
  onCompanySelect,
  onManualSearch,
}: SearchCommandProps) {
  const [internalValue, setInternalValue] = useState("");
  const [isSelected, setIsSelected] = useState(false);

  const value = controlledValue !== undefined ? controlledValue : internalValue;
  const setValue = (newValue: string) => {
    if (onChange) {
      onChange(newValue);
    } else {
      setInternalValue(newValue);
    }
  };

  const filteredCompanies = useMemo(() => {
    if (!value.trim()) return [];
    const searchTerm = value.toLowerCase();
    return companies.filter(
      (company) =>
        company.name.toLowerCase().includes(searchTerm) ||
        company.shortName.toLowerCase().includes(searchTerm) ||
        company.industry.toLowerCase().includes(searchTerm)
    );
  }, [value]);

  const handleValueChange = (newValue: string) => {
    setValue(newValue);
    setIsSelected(false);
  };

  const handleSelect = (selectedValue: string) => {
    setValue(selectedValue);
    setIsSelected(true);

    // Find the selected company and pass its data
    const selectedCompany = companies.find(
      (company) => company.name.toLowerCase() === selectedValue.toLowerCase()
    );
    if (selectedCompany && onCompanySelect) {
      onCompanySelect({
        name: selectedCompany.name,
        sector: selectedCompany.industry,
      });
    }
  };

  const handleSelectCurrentValue = () => {
    if (value.trim()) {
      setIsSelected(true);
      if (onCompanySelect) {
        onCompanySelect({
          name: value.trim(),
          sector: "Otro",
        });
      }
    }
  };

  return (
    <Command className="rounded-lg border shadow-md">
      <CommandInput
        placeholder="Buscar empresa..."
        value={value}
        onValueChange={handleValueChange}
      />
      {value.length > 0 && !isSelected && (
        <CommandList>
          <CommandEmpty>
            <div className="flex items-center justify-center gap-1 py-4">
              <span className="text-sm text-muted-foreground">
                No encuentro la empresa.
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleSelectCurrentValue}
                className="h-auto p-0 text-sm font-normal text-primary hover:bg-transparent hover:underline"
              >
                Seleccionar el mismo
              </Button>
            </div>
          </CommandEmpty>
          <CommandGroup heading="Empresas">
            {filteredCompanies.map((company) => (
              <CommandItem
                key={company.shortName}
                value={company.name}
                onSelect={handleSelect}
              >
                {company.logo ? (
                  <img
                    src={company.logo}
                    alt={company.shortName}
                    className="mr-2 h-5 w-5 object-contain"
                  />
                ) : (
                  <Building2 className="mr-2 h-5 w-5 text-muted-foreground" />
                )}
                <div className="flex flex-col">
                  <span className="font-medium">{company.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {company.industry}
                  </span>
                </div>
              </CommandItem>
            ))}
          </CommandGroup>
        </CommandList>
      )}
    </Command>
  );
}
