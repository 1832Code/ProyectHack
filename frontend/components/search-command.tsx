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
    <Command className="rounded-2xl border border-white/20 bg-white/5 backdrop-blur-sm overflow-hidden [&_[data-slot=command-input-wrapper]]:border-b-0 [&_[data-slot=command-input-wrapper]]:h-14 [&_[data-slot=command-input-wrapper]]:px-4 [&_[data-slot=command-input-wrapper]]:gap-3 [&_[data-slot=command-input-wrapper]_svg]:size-5 [&_[data-slot=command-input-wrapper]_svg]:text-gray-400 [&_[data-slot=command-input-wrapper]_svg]:opacity-100">
      <CommandInput
        placeholder="Ej: Mi Empresa S.A.C."
        value={value}
        onValueChange={handleValueChange}
        className="!h-14 text-base text-white placeholder:text-gray-400"
      />
      {value.length > 0 && !isSelected && (
        <CommandList className="border-t border-white/10 max-h-[250px]">
          <CommandEmpty>
            <div className="flex flex-col items-center justify-center gap-2 py-6">
              <span className="text-sm text-gray-400">
                No encontramos esa empresa
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleSelectCurrentValue}
                className="h-auto px-3 py-1.5 text-sm font-medium text-cyan-400 hover:text-cyan-300 hover:bg-cyan-500/10 rounded-lg transition-colors"
              >
                Usar "{value}" de todos modos
              </Button>
            </div>
          </CommandEmpty>
          <CommandGroup heading="Empresas sugeridas" className="text-gray-400">
            {filteredCompanies.map((company) => (
              <CommandItem
                key={company.shortName}
                value={company.name}
                onSelect={handleSelect}
                className="py-3 px-3 mx-1 my-0.5 rounded-xl text-white cursor-pointer transition-colors data-[selected=true]:bg-gradient-to-r data-[selected=true]:from-cyan-500/20 data-[selected=true]:to-purple-500/20 data-[selected=true]:text-cyan-300 hover:bg-white/10"
              >
                {company.logo ? (
                  <img
                    src={company.logo}
                    alt={company.shortName}
                    className="mr-3 h-8 w-8 rounded-lg object-contain bg-white/10 p-1"
                  />
                ) : (
                  <div className="mr-3 h-8 w-8 rounded-lg bg-gradient-to-br from-cyan-500/20 to-purple-500/20 flex items-center justify-center">
                    <Building2 className="h-4 w-4 text-cyan-400" />
                  </div>
                )}
                <div className="flex flex-col">
                  <span className="font-medium">{company.name}</span>
                  <span className="text-xs text-gray-200">
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
