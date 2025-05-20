<?php

namespace App\Filament\Resources\CajaDiariaResource\Pages;

use App\Filament\Resources\CajaDiariaResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListCajaDiarias extends ListRecords
{
    protected static string $resource = CajaDiariaResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make(),
        ];
    }
}
