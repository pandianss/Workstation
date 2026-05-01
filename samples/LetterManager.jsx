import React, { useState } from 'react';
import LetterList from './LetterList';
import LetterForm from './LetterForm';

const LetterManager = () => {
    // Mode: 'list' | 'create' | 'edit'
    const [mode, setMode] = useState('list');
    const [selectedLetter, setSelectedLetter] = useState(null);

    return (
        <div style={{ position: 'relative' }}>
            {mode === 'list' && (
                <LetterList
                    onCreateNew={() => {
                        setSelectedLetter(null);
                        setMode('create');
                    }}
                    onSelect={(letter) => {
                        setSelectedLetter(letter);
                        setMode('edit');
                    }}
                />
            )}

            {(mode === 'create' || mode === 'edit') && (
                <LetterForm
                    onBack={() => {
                        setMode('list');
                        setSelectedLetter(null);
                    }}
                    initialData={selectedLetter}
                />
            )}
        </div>
    );
};

export default LetterManager;
